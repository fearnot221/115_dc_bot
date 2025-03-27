import discord
from discord import app_commands
from discord.ext import commands
from bot import is_admin
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

async def setup(bot):
    await bot.add_cog(Emoji(bot))
