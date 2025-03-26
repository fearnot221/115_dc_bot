import discord
from discord import app_commands
from discord.ext import commands
from main import is_admin
from database.db_manager import DatabaseManager


class Emoji(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db_manager = None
    
    @app_commands.command(name="add_emoji", description="添加表情到全局配置中")
    @is_admin()
    async def add_emoji(self, interaction: discord.Interaction, name: str, emoji: str):
        """添加表情到全局配置中
        
        Args:
            name: 表情的名稱
            emoji: Discord 表情（直接輸入表情或使用表情ID）
        """
            
        # 初始化資料庫管理器
        db = DatabaseManager(interaction.guild_id, interaction.guild.name)
        
        # 解析表情ID
        if emoji.isdigit():
            # 如果輸入的是ID
            emoji_id = int(emoji)
            emoji = f"<a:{name}:{emoji_id}>"
        else:
            # 如果輸入的是表情
            # 使用正則表達式從表情格式中提取ID
            import re
            match = re.search(r'<a?:\w+:(\d+)>', emoji)
            if not match:
                await interaction.response.send_message("❌ 無效的表情格式。請直接輸入表情或使用表情ID。", ephemeral=True)
                return
            emoji_id = int(match.group(1))

        # 保存表情配置
        await db.save_emoji(name, emoji_id, emoji)
        
        await interaction.response.send_message(f"✅ 已添加表情 `{name}` 到全局配置中", ephemeral=True)

    @app_commands.command(name="remove_emoji", description="從全局配置中移除表情")
    @is_admin()
    async def remove_emoji(self, interaction: discord.Interaction, name: str):
        """從全局配置中移除表情
        
        Args:
            name: 要移除的表情名稱
        """
        # 檢查是否為管理員
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ 你沒有權限執行此指令", ephemeral=True)
            return
            
        # 初始化資料庫管理器
        db = DatabaseManager(interaction.guild_id, interaction.guild.name)
        
        # 移除表情
        if await db.remove_emoji(name):
            await interaction.response.send_message(f"✅ 已從全局配置中移除表情 `{name}`", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ 找不到名為 `{name}` 的表情", ephemeral=True)

    @app_commands.command(name="list_emojis", description="列出所有已配置的表情")
    @is_admin()
    async def list_emojis(self, interaction: discord.Interaction):
        """列出所有已配置的表情"""
        # 檢查是否為管理員
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ 你沒有權限執行此指令", ephemeral=True)
            return
            
        # 初始化資料庫管理器
        db = DatabaseManager(interaction.guild_id, interaction.guild.name)
        
        # 獲取所有表情
        emojis = await db.get_all_emojis()
        
        if not emojis:
            await interaction.response.send_message("❌ 目前沒有配置任何表情", ephemeral=True)
            return
            
        # 創建表情列表訊息
        message = "📋 已配置的表情列表\n\n"
        
        # 添加每個表情的資訊
        for name, emoji_info in emojis.items():
            message += f"{emoji_info['format']} | name:**{name}** | id:{emoji_info['id']}\n\n"
        
        await interaction.response.send_message(message, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Emoji(bot))
    