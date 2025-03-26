import discord
from discord import app_commands
from discord.ext import commands
from main import is_admin
from database.db_manager import DatabaseManager    
    
class Delete_Channel(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db_manager = None
    
    async def ensure_db_manager(self, interaction: discord.Interaction):
        """Ensure that db_manager is initialized for the current guild"""
        guild_id = interaction.guild.id
        guild_name = interaction.guild.name
        
        # If db_manager is None or for a different guild, initialize it
        if (self.db_manager is None or 
            self.db_manager.guild_id != guild_id):
            self.db_manager = DatabaseManager(guild_id, guild_name)
            await self.db_manager.init_db()
            
            # Also update the application category ID
            self.application_category_id = await self.db_manager.get_application_category()
            
        return self.db_manager
    
    
    
    @app_commands.command(name="delete_channel", description="刪除當前頻道（僅限機器人創建的頻道）")
    @is_admin()
    async def delete_channel(self, interaction: discord.Interaction):
        """Delete the current channel if it was created by the bot"""
        await interaction.response.defer(ephemeral=True)
        
        # Ensure db_manager is initialized
        await self.ensure_db_manager(interaction)
        
        # 檢查是否是機器人創建的頻道
        is_bot_channel = await self.db_manager.is_bot_created_channel(interaction.channel.id)
        
        if not is_bot_channel:
            embed = discord.Embed(
                title="無法刪除",
                description="此頻道不是由機器人創建的，無法使用此命令刪除。",
                color=discord.Color.red()
            )
            return await interaction.followup.send(embed=embed, ephemeral=True)
        
        # 檢查用戶是否有權限刪除（是申請人或管理員）
        channel_data = None
        for member in self.bot.guilds[0].members:
            user_channel = await self.db_manager.get_application_channel(member.id)
            if user_channel and user_channel["channel_id"] == interaction.channel.id:
                channel_data = user_channel
                application_owner_id = member.id
                break
        
        # 如果找不到對應的申請數據，則檢查頻道名稱
        if not channel_data and interaction.channel.name.startswith("申請-"):
            # 從頻道名稱中提取用戶名
            user_display_name = interaction.channel.name[3:]  # 去掉 "申請-" 前綴
            # 嘗試找到與名稱匹配的用戶
            for member in interaction.guild.members:
                if member.display_name.lower() == user_display_name.lower():
                    application_owner_id = member.id
                    break
            else:
                # 沒有找到匹配的用戶，設為 None
                application_owner_id = None
        elif not channel_data:
            # 如果不是申請頻道但是機器人創建的，允許管理員刪除
            application_owner_id = None
        
        # 檢查權限
        is_admin = interaction.user.guild_permissions.administrator
        is_owner = application_owner_id and interaction.user.id == application_owner_id
        
        if not (is_admin or is_owner):
            embed = discord.Embed(
                title="權限不足",
                description="只有頻道申請人或管理員可以刪除此頻道。",
                color=discord.Color.red()
            )
            return await interaction.followup.send(embed=embed, ephemeral=True)
        
        # 刪除頻道
        embed = discord.Embed(
            title="頻道將被刪除",
            description="頻道將在3秒後刪除...",
            color=discord.Color.orange()
        )
        
        # 如果有對應的申請，更新申請狀態
        if application_owner_id:
            await self.db_manager.update_application_status(application_owner_id, "closed")
        
        # 從機器人創建的頻道列表中移除
        await self.db_manager.remove_bot_created_channel(interaction.channel.id)
        
        # Send deletion message to the channel
        await interaction.followup.send(embed=embed)
        
        # 添加小延遲後刪除
        import asyncio
        await asyncio.sleep(3)
        
        await interaction.channel.delete()
        
async def setup(bot):
    await bot.add_cog(Delete_Channel(bot))
