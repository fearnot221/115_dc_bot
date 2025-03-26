import discord
from discord import app_commands
from discord.ext import commands
from bot import is_admin
from database.db_manager import DatabaseManager
from discord.ui import Modal, TextInput


class RejectionReasonModal(Modal):
    """Modal for entering rejection reason"""
    def __init__(self, user_id: int, cog: 'Manage_Application'):
        super().__init__(title="拒絕申請原因")
        self.user_id = user_id
        self.cog = cog
        
        self.reason = TextInput(
            label="拒絕原因",
            placeholder="請輸入拒絕此申請的原因",
            required=True,
            style=discord.TextStyle.paragraph
        )
        
        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction):
        """Handle rejection reason submission"""
        # Get the user
        user = interaction.guild.get_member(self.user_id)
        
        if not user:
            return await interaction.response.send_message("找不到該用戶，可能已經離開伺服器。", ephemeral=True)
            
        # Update database
        await self.cog.db_manager.update_application_status(self.user_id, "rejected")
        
        # Get the user's application channel
        channel_data = await self.cog.db_manager.get_application_channel(self.user_id)
        channel = interaction.guild.get_channel(channel_data["channel_id"]) if channel_data else None
        
        # Send notification in the application channel
        if channel:
            embed_channel = discord.Embed(
                title="申請已拒絕",
                description=f"{interaction.user.mention} 已拒絕此申請。",
                color=discord.Color.red()
            )
            
            embed_channel.add_field(
                name="拒絕原因",
                value=self.reason.value,
                inline=False
            )
            
            await channel.send(embed=embed_channel)
        
        # Send confirmation to admin
        embed = discord.Embed(
            title="狀態已更新",
            description=f"{user.mention} 的申請已拒絕。",
            color=discord.Color.red()
        )
        
        embed.add_field(
            name="拒絕原因",
            value=self.reason.value,
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


class Manage_Application(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db_manager = None

    async def ensure_db_manager(self, interaction: discord.Interaction):
        """Ensure that db_manager is initialized for the current guild"""
        guild_id = interaction.guild.id
        guild_name = interaction.guild.name
        
        # Initialize db_manager if needed
        if (self.db_manager is None or 
            self.db_manager.guild_id != guild_id):
            self.db_manager = DatabaseManager(guild_id, guild_name)
            await self.db_manager.init_db()
            
        return self.db_manager
    
    async def is_application_channel(self, channel_id: int, interaction: discord.Interaction) -> bool:
        """Check if the current channel is an application channel"""
        db_manager = await self.ensure_db_manager(interaction)
        
        # Check if this is a bot-created channel
        is_bot_channel = await db_manager.is_bot_created_channel(channel_id)
        
        # If it's a bot-created channel, also check if it's specifically an application channel
        if is_bot_channel:
            # Check if the channel name starts with "申請-" (application-)
            channel = interaction.guild.get_channel(channel_id)
            if channel and channel.name.startswith("申請-"):
                return True
                
            # Check if the channel is linked to any user's application
            for member in interaction.guild.members:
                user_channel = await db_manager.get_application_channel(member.id)
                if user_channel and user_channel["channel_id"] == channel_id:
                    return True
        
        return False
    
    async def get_channel_owner(self, channel_id: int, interaction: discord.Interaction) -> discord.Member:
        """Get the owner of the application channel"""
        db_manager = await self.ensure_db_manager(interaction)
        
        # First check if the channel is linked to any user's application
        for member in interaction.guild.members:
            user_channel = await db_manager.get_application_channel(member.id)
            if user_channel and user_channel["channel_id"] == channel_id:
                return member
        
        # If not found through database, try to get from channel name
        channel = interaction.guild.get_channel(channel_id)
        if channel and channel.name.startswith("申請-"):
            # Extract username from channel name (remove "申請-" prefix)
            user_display_name = channel.name[3:]
            
            # Find the member with this display name
            for member in interaction.guild.members:
                if member.display_name.lower() == user_display_name.lower():
                    return member
        
        return None
    
    async def show_role_selection(self, interaction: discord.Interaction, user_id: int):
        """Show role selection dropdown with available roles from JSON"""
        # Initialize DatabaseManager
        db_manager = await self.ensure_db_manager(interaction)
        
        # Get all available roles
        available_roles = await db_manager.get_available_roles()
        
        if not available_roles:
            embed = discord.Embed(
                title="錯誤",
                description="找不到任何可用的身份組。請先在配置中設置可用的身份組。",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        # Create selection menu, set max_values to allow multiple selections
        select = discord.ui.Select(
            placeholder="選擇要賦予的身份組",
            custom_id=f"role_select_{user_id}",
            options=[
                discord.SelectOption(
                    label=role["name"],
                    value=str(role["id"]),
                    description=f"賦予 {role['name']} 身份組"
                )
                for role in available_roles
            ],
            max_values=len(available_roles)  # Allow selecting up to all available roles
        )
        
        async def role_select_callback(select_interaction):
            role_ids = [int(value) for value in select_interaction.data["values"]]
            
            # Get the applicant
            applicant = interaction.guild.get_member(user_id)
            if not applicant:
                await select_interaction.response.send_message("找不到申請者，可能已經離開伺服器。", ephemeral=True)
                return
            
            try:
                # Update database
                await db_manager.update_application_status(user_id, "approved")
                
                added_roles = []
                failed_roles = []
                
                # Process each selected role
                for role_id in role_ids:
                    role = interaction.guild.get_role(role_id)
                    if not role:
                        failed_roles.append(f"ID: {role_id}")
                        continue
                    
                    # Save verification role
                    try:
                        await db_manager.save_verification_role(str(user_id), role.id, role.name)
                        added_roles.append(role.mention)
                    except Exception as e:
                        failed_roles.append(f"{role.name} ({str(e)})")
                
                # Create notification embed
                embed = discord.Embed(
                    title="申請已批准",
                    description=f"{applicant.mention} 的申請已批准！",
                    color=discord.Color.green()
                )
                
                if added_roles:
                    embed.add_field(
                        name="已設置的身份組",
                        value="\n".join(added_roles),
                        inline=False
                    )
                
                if failed_roles:
                    embed.add_field(
                        name="設置失敗的身份組",
                        value="\n".join(failed_roles),
                        inline=False
                    )
                
                # Send notification
                await select_interaction.response.send_message(embed=embed, ephemeral=True)
                
                # Get the channel and send notification there too
                channel_data = await db_manager.get_application_channel(user_id)
                if channel_data:
                    channel = interaction.guild.get_channel(channel_data["channel_id"])
                    if channel:
                        # Send notification in the channel
                        channel_embed = discord.Embed(
                            title="申請已批准",
                            description=f"{select_interaction.user.mention} 已批准此申請。",
                            color=discord.Color.green()
                        )
                        
                        if added_roles:
                            channel_embed.add_field(
                                name="已設置的身份組",
                                value="\n".join(added_roles),
                                inline=False
                            )
                        
                        # Send instruction embed
                        instruction_embed = discord.Embed(
                            title="下一步",
                            description="請回到機器人的驗證按鈕處點擊「驗證身份」按鈕來獲取您的身份組。",
                            color=discord.Color.blue()
                        )
                        
                        await channel.send(content=applicant.mention, embed=channel_embed)
                        await channel.send(embed=instruction_embed)
                
            except Exception as e:
                await select_interaction.response.send_message(f"設置身份組時發生錯誤: {str(e)}", ephemeral=True)
        
        # Set the callback
        select.callback = role_select_callback
        
        # Create view and add the select menu
        view = discord.ui.View(timeout=None)
        view.add_item(select)
        
        # Send the message with the view
        embed = discord.Embed(
            title="批准申請",
            description=f"請選擇要賦予給申請者的身份組（可複選）：",
            color=discord.Color.blue()
        )
        
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

    @app_commands.command(name="manage_application", description="管理當前申請頻道的申請")
    @app_commands.choices(action=[
        app_commands.Choice(name="關閉申請", value="close"),
        app_commands.Choice(name="批准申請", value="approve"),
        app_commands.Choice(name="拒絕申請", value="reject")
    ])
    @is_admin()
    async def manage_application(self, interaction: discord.Interaction, action: app_commands.Choice[str]):
        """Manage application in the current channel with dropdown selection for actions"""
        action_value = action.value  # Extract the value from the Choice object
        
        # Handle reject action differently - must be done before defer
        if action_value == "reject":
            # For reject, we need to show a modal before any other response
            # Get the channel owner first
            await self.ensure_db_manager(interaction)
            
            # Check if this command is being used in an application channel
            if not await self.is_application_channel(interaction.channel_id, interaction):
                embed = discord.Embed(
                    title="指令限制",
                    description="此指令只能在申請頻道中使用。",
                    color=discord.Color.red()
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)
                
            # Get the application owner from the current channel
            user = await self.get_channel_owner(interaction.channel_id, interaction)
            
            if not user:
                embed = discord.Embed(
                    title="找不到申請人",
                    description="無法確定此頻道的申請人。請確認頻道是否為有效的申請頻道。",
                    color=discord.Color.red()
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)
                
            # Show rejection reason modal directly without defer
            modal = RejectionReasonModal(user.id, self)
            return await interaction.response.send_modal(modal)
            
        # For other actions (close, approve), we can defer first
        await interaction.response.defer(ephemeral=True)
        
        # Ensure db_manager is initialized
        await self.ensure_db_manager(interaction)
        
        # Check if this command is being used in an application channel
        if not await self.is_application_channel(interaction.channel_id, interaction):
            embed = discord.Embed(
                title="指令限制",
                description="此指令只能在申請頻道中使用。",
                color=discord.Color.red()
            )
            return await interaction.followup.send(embed=embed, ephemeral=True)
        
        # Get the application owner from the current channel
        user = await self.get_channel_owner(interaction.channel_id, interaction)
        
        if not user:
            embed = discord.Embed(
                title="找不到申請人",
                description="無法確定此頻道的申請人。請確認頻道是否為有效的申請頻道。",
                color=discord.Color.red()
            )
            return await interaction.followup.send(embed=embed, ephemeral=True)
        
        # Get user's application channel data
        channel_data = await self.db_manager.get_application_channel(user.id)
        
        if not channel_data:
            embed = discord.Embed(
                title="找不到申請",
                description=f"找不到 {user.mention} 的申請記錄。",
                color=discord.Color.red()
            )
            return await interaction.followup.send(embed=embed, ephemeral=True)
        
        channel = interaction.guild.get_channel(channel_data["channel_id"])
        
        if action_value == "close":
            # Instead of deleting the channel, remove the applicant's permissions
            if channel:
                # Edit channel permissions to remove the applicant
                overwrites = channel.overwrites
                if user in overwrites:
                    del overwrites[user]
                    await channel.edit(overwrites=overwrites)
                    
                    # Send a notification in the channel
                    embed_channel = discord.Embed(
                        title="申請已關閉",
                        description=f"{interaction.user.mention} 已關閉此申請。申請者已無法存取此頻道。",
                        color=discord.Color.blue()
                    )
                    await channel.send(embed=embed_channel)
            
            # Update the application status in the database
            await self.db_manager.update_application_status(user.id, "closed")
            
            # Send confirmation to admin
            embed = discord.Embed(
                title="申請已關閉",
                description=f"{user.mention} 的申請已關閉，申請者已無法存取頻道。",
                color=discord.Color.green()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        elif action_value == "approve":
            # Show role selection menu instead of immediate approval
            return await self.show_role_selection(interaction, user.id)
            
        else:
            embed = discord.Embed(
                title="無效的操作",
                description="有效的操作有：close, approve, reject",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
        
async def setup(bot):
    await bot.add_cog(Manage_Application(bot))



