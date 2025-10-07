import discord
from discord.ui import Button, View
from database.db_manager import DatabaseManager
import asyncio
import colorsys

# 領取身份組按鈕面板
class Gay(View):
    def __init__(self, bot=None):
        super().__init__(timeout=None)
        self.bot = bot
        self.emoji = self.bot.emoji
        
        button = Button(
            label="多元身份認同", 
            style=discord.ButtonStyle.primary,
            emoji=self.emoji.get('gay3'),
            custom_id="role_button_gay"
        )
        button.callback = self.button_callback
        
        self.add_item(button)
    
    # 驗證身份功能
    async def button_callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        db_manager = DatabaseManager(interaction.guild.id, interaction.guild.name)
        
        role_id = await db_manager.get_role_id_config(role_name="gay")

        role = interaction.guild.get_role(role_id)
        
        if role:
            if not role in interaction.user.roles:
                
                await interaction.user.add_roles(role)
            
                embed = discord.Embed(
                    title="認同成功",
                    description=f"恭喜 {self.emoji.get('gay4')}",
                    color=0xFF0000
                )

                msg = await interaction.followup.send(embed=embed, ephemeral=True)
                
                while True:
                    for h in range(0, 361, 5):  # 色相 H 從 0° 變到 360°
                        r, g, b = colorsys.hsv_to_rgb(h / 360, 1, 1)  # 轉 RGB
                        hex_color = (int(r * 255) << 16) + (int(g * 255) << 8) + int(b * 255)
                        await msg.edit(embed=discord.Embed(
                            title="認同成功",
                            description=f"恭喜 {self.emoji.get('gay4')}",
                            color=hex_color
                        ))
                        await asyncio.sleep(0.1)  # 調整變色速度
            else:
                
                await interaction.user.remove_roles(role)
            
                embed = discord.Embed(
                    title="嗚嗚嗚已不認同",
                    description=f"為什麼不認同 TT {self.emoji.get('gay4')}",
                    color=0xFF0000
                )

                msg = await interaction.followup.send(embed=embed, ephemeral=True)
                
                while True:
                    for h in range(0, 361, 5):  # 色相 H 從 0° 變到 360°
                        r, g, b = colorsys.hsv_to_rgb(h / 360, 1, 1)  # 轉 RGB
                        hex_color = (int(r * 255) << 16) + (int(g * 255) << 8) + int(b * 255)
                        await msg.edit(embed=discord.Embed(
                            title="嗚嗚嗚已不認同",
                            description=f"為什麼不認同 TT {self.emoji.get('gay4')}",
                            color=hex_color
                        ))
                        await asyncio.sleep(0.1)  # 調整變色速度

class Crown(View):
    def __init__(self, bot=None):
        super().__init__(timeout=None)
        self.bot = bot
        self.emoji = self.bot.emoji
        
        button = Button(
            label="多元身份認同", 
            style=discord.ButtonStyle.primary,
            emoji=self.emoji.get('crown1'),
            custom_id="role_button_crown"
        )
        button.callback = self.button_callback
        
        self.add_item(button)
    
    # 驗證身份功能
    async def button_callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        db_manager = DatabaseManager(interaction.guild.id, interaction.guild.name)
        
        role_id = await db_manager.get_role_id_config(role_name="crown")

        role = interaction.guild.get_role(role_id)
        
        if role:
            if not role in interaction.user.roles:
                
                await interaction.user.add_roles(role)
            
                embed = discord.Embed(
                    title="認同成功",
                    description=f"恭喜 {self.emoji.get('crown1')}",
                    color=0xFF0000
                )

                msg = await interaction.followup.send(embed=embed, ephemeral=True)
                
                while True:
                    for h in range(0, 361, 5):  # 色相 H 從 0° 變到 360°
                        r, g, b = colorsys.hsv_to_rgb(h / 360, 1, 1)  # 轉 RGB
                        hex_color = (int(r * 255) << 16) + (int(g * 255) << 8) + int(b * 255)
                        await msg.edit(embed=discord.Embed(
                            title="認同成功",
                            description=f"恭喜 {self.emoji.get('crown1')}",
                            color=hex_color
                        ))
                        await asyncio.sleep(0.1)  # 調整變色速度
            else:
                
                await interaction.user.remove_roles(role)
            
                embed = discord.Embed(
                    title="嗚嗚嗚已不認同",
                    description=f"為什麼不認同 TT {self.emoji.get('crown1')}",
                    color=0xFF0000
                )

                msg = await interaction.followup.send(embed=embed, ephemeral=True)
                
                while True:
                    for h in range(0, 361, 5):  # 色相 H 從 0° 變到 360°
                        r, g, b = colorsys.hsv_to_rgb(h / 360, 1, 1)  # 轉 RGB
                        hex_color = (int(r * 255) << 16) + (int(g * 255) << 8) + int(b * 255)
                        await msg.edit(embed=discord.Embed(
                            title="嗚嗚嗚已不認同",
                            description=f"為什麼不認同 TT {self.emoji.get('crown1')}",
                            color=hex_color
                        ))
                        await asyncio.sleep(0.1)  # 調整變色速度

class Cat(View):
    def __init__(self, bot=None):
        super().__init__(timeout=None)
        self.bot = bot
        self.emoji = self.bot.emoji
        
        button = Button(
            label="貓貓教", 
            style=discord.ButtonStyle.primary,
            emoji=self.emoji.get('cat1-2'),
            custom_id="role_button_cat"
        )
        button.callback = self.button_callback
        
        self.add_item(button)
    
    # 驗證身份功能
    async def button_callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        db_manager = DatabaseManager(interaction.guild.id, interaction.guild.name)
        
        role_id = await db_manager.get_role_id_config(role_name="cat")

        role = interaction.guild.get_role(role_id)
        
        if role:
            if not role in interaction.user.roles:
                
                await interaction.user.add_roles(role)
            
                embed = discord.Embed(
                    title="入教成功",
                    description=f"恭喜 {self.emoji.get('cat2')}",
                    color=0xFF0000
                )

                msg = await interaction.followup.send(embed=embed, ephemeral=True)
                
                while True:
                    for h in range(0, 361, 5):  # 色相 H 從 0° 變到 360°
                        r, g, b = colorsys.hsv_to_rgb(h / 360, 1, 1)  # 轉 RGB
                        hex_color = (int(r * 255) << 16) + (int(g * 255) << 8) + int(b * 255)
                        await msg.edit(embed=discord.Embed(
                            title="入教成功",
                            description=f"恭喜 {self.emoji.get('cat2')}",
                            color=hex_color
                        ))
                        await asyncio.sleep(0.1)  # 調整變色速度
            else:
                
                await interaction.user.remove_roles(role)
            
                embed = discord.Embed(
                    title="嗚嗚嗚已退出貓貓教",
                    description=f"為什麼要退出 TT {self.emoji.get('cat3')}",
                    color=0xFF0000
                )

                msg = await interaction.followup.send(embed=embed, ephemeral=True)
                
                while True:
                    for h in range(0, 361, 5):  # 色相 H 從 0° 變到 360°
                        r, g, b = colorsys.hsv_to_rgb(h / 360, 1, 1)  # 轉 RGB
                        hex_color = (int(r * 255) << 16) + (int(g * 255) << 8) + int(b * 255)
                        await msg.edit(embed=discord.Embed(
                            title="嗚嗚嗚已退出貓貓教",
                            description=f"為什麼要退出 TT {self.emoji.get('cat3')}",
                            color=hex_color
                        ))
                        await asyncio.sleep(0.1)  # 調整變色速度

# 初始化函數，用於重啟 bot 時註冊所有持久化視圖
def setup_persistent_views_role_button(bot):
    try:
        
        bot.add_view(Gay(bot=bot))
        
        bot.add_view(Crown(bot=bot))
        
        bot.add_view(Cat(bot=bot))
        
        return True
    except Exception as e:
        print(f"設定持久化視圖時發生錯誤: {e}")
        return False