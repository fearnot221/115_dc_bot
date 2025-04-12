import discord
from discord import app_commands
from discord.ext import commands
from utils.mcserver_ui import Mcserver
from bot import is_admin

class Mcserver_Setup(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.emoji = self.bot.emoji
    
    @app_commands.command(name="mcserver_setup", description="建立麥塊伺服器控制面板")
    @is_admin()
    async def setup_buttons(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title=f"{self.emoji.get('minecraft')} 麥塊伺服器控制面板",
            description="🖥️ 讀取伺服器狀態中...",
            color=discord.Color.blue()
        )
        msg = await interaction.response.send_message(embed=embed, wait=True)
        view = Mcserver(bot=self.bot, message=msg)
        await view.update_panel()  


async def setup(bot):
    await bot.add_cog(Mcserver_Setup(bot))