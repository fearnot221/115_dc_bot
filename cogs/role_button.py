import discord
from discord import app_commands
from discord.ext import commands
from utils.role_button_ui import Main
from bot import is_admin
import asyncio
import colorsys


class Role_Button(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.emoji = self.bot.emoji
    
    @app_commands.command(name="role_button", description="建立領取身份組按鈕")
    @is_admin()
    async def setup_buttons(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title=f"{self.emoji.get('gay1')} 多元身份認同",
            description=f"我們支持多元身份認同\n\n歡迎 {self.emoji.get('gay2')}",
            color=0xFF0000
        )
        
        view = Main(bot=self.bot)
        await interaction.response.send_message(embed=embed, view=view)
            
        while True:
            for h in range(0, 361, 5):  # 色相 H 從 0° 變到 360°
                r, g, b = colorsys.hsv_to_rgb(h / 360, 1, 1)  # 轉 RGB
                hex_color = (int(r * 255) << 16) + (int(g * 255) << 8) + int(b * 255)
                await interaction.edit_original_response(embed=discord.Embed(
                    title=f"{self.emoji.get('gay1')} 多元身份認同",
                    description=f"我們支持多元身份認同\n\n歡迎 {self.emoji.get('gay2')}",
                    color=hex_color
                ))
                await asyncio.sleep(0.1)  # 調整變色速度


async def setup(bot):
    await bot.add_cog(Role_Button(bot))