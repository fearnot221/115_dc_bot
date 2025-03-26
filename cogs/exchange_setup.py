import discord
from discord import app_commands
from discord.ext import commands
from utils.exchange_ui import Exchange_View
from main import is_admin

class Exchange_Setup(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.emoji = self.bot.emoji
    
    @app_commands.command(name="exchange_setup", description="建立交換備審申請面板")
    @is_admin()
    async def setup_buttons(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title=f"{self.emoji.get('cheers')} 交換備審申請",
            description=f"按 F 進入申請",
            color=discord.Color.blue()
        )
        
        view = Exchange_View(bot=self.bot)
        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Exchange_Setup(bot))