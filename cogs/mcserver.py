import discord
from discord import app_commands
from discord.ext import commands
from utils.mcserver_ui import Mcserver
from bot import is_admin
from database.db_manager import DatabaseManager

class Mcserver_Setup(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.emoji = self.bot.emoji
        self.db_manager = None
    
    @app_commands.command(name="mcserver_setup", description="建立麥塊伺服器控制面板")
    @is_admin()
    async def setup_buttons(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title=f"{self.emoji.get('minecraft')} 麥塊伺服器控制面板",
            description=f"{self.emoji.get('green_fire')} **開機**\n\n{self.emoji.get('red_fire')} **關機**",
            color=discord.Color.blue()
        )
        
        await interaction.response.defer()  # 先延遲回應，接著使用 followup

        view = Mcserver(bot=self.bot)
        msg = await interaction.followup.send(embed=embed, view=view, wait=True)

        view.message = msg  # 設定 message 屬性給 Mcserver 使用
        await view.update_panel()  # 初始化狀態

    @app_commands.command(name="mcserver_status", description="查詢並更新麥塊伺服器控制面板")
    @is_admin()
    async def status_panel(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        db = DatabaseManager(interaction.guild_id, interaction.guild.name, )
        
        message_id = await db.get_mcserver_message()
        
        message = interaction.channel.fetch_message(message_id)
        
        view = Mcserver(bot=self.bot, message=message)
        
        await view.update_panel()

        await interaction.followup.send("✅ 已更新控制面板狀態！", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Mcserver_Setup(bot))