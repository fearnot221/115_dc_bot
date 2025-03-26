from discord.ext import commands
from database.db_manager import DatabaseManager

class IdentityManagement(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db_manager = None
        self.application_category_id = None

    async def setup_db(self, guild_id: int):
        # 獲取伺服器物件
        guild = self.bot.get_guild(guild_id)
        guild_name = guild.name if guild else None
        
        # 初始化數據管理器，傳入伺服器名稱
        self.db_manager = DatabaseManager(guild_id, guild_name)
        await self.db_manager.init_db()
        
        # 從配置中讀取應用類別 ID
        self.application_category_id = await self.db_manager.get_application_category()
    
    async def cogs_load(self, guild_id: int):
        """Called when the cog is loaded"""
        
        guild = self.bot.get_guild(guild_id)
        guild_name = guild.name if guild else None
        
        for guild in self.bot.guilds:
            try:
                await self.setup_db(guild_id)
                print(f"已為伺服器 {guild_name} (ID: {guild_id}) 初始化資料庫和類別 ID")
                if self.application_category_id:
                    category = guild.get_channel(self.application_category_id)
                    if category:
                        print(f"已載入申請類別: {category.name} (ID: {category.id})")
                    else:
                        print(f"警告: 找不到設定的申請類別 (ID: {self.application_category_id})")
            except Exception as e:
                print(f"初始化伺服器 {guild_name} (ID: {guild_id}) 時發生錯誤: {str(e)}")

async def setup(bot):
    await bot.add_cog(IdentityManagement(bot))