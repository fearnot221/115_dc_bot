import discord
from discord import app_commands
from discord.ext import commands
from utils.role_ui import Verfication_View
from bot import is_admin

class Mcserver_Setup(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.emoji = self.bot.emoji
    
    @app_commands.command(name="role_setup", description="建立麥塊伺服器控制面板")
    @is_admin()
    async def setup_buttons(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title=f"{self.emoji.get('minecraft')} 麥塊伺服器控制面板",
            description=f"{self.emoji.get('green_fire')} **開機**\n\n{self.emoji.get('red_fire')} **關機**",
            color=discord.Color.blue()
        )
        
        view = Verfication_View(bot=self.bot)
        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Mcserver_Setup(bot))