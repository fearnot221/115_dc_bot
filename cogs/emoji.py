import discord
from discord import app_commands
from discord.ext import commands
from bot import is_admin
from database.db_manager import DatabaseManager


class Emoji(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db_manager = None

        self.happymention = app_commands.ContextMenu(name='happymention', callback=self.mention_callback)
        self.bot.tree.add_command(self.happymention)

        self.angrymention = app_commands.ContextMenu(name='angrymention', callback=self.mention_callback)
        self.bot.tree.add_command(self.angrymention)

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

    async def mention_callback(self, interaction: discord.Interaction, message: discord.Message):
        await interaction.response.defer(ephemeral=True, thinking=True)

        if interaction.command.name == 'happymention':
            emojis = [
                '<:happy_mention_1:1409478991978561546>',
                '<:happy_mention_2:1409479101244243989>',
                '<:happy_mention_3:1409479817895608391>',
                '<:happy_mention_4:1409479841660538981>',
                '<:happy_mention_5:1409479864108716052>',
                '<:happy_mention_6:1409479883700179004>',
                '<:happy_mention_7:1409479903409340510>',
                '<:happy_mention_8:1409479924380598332>',
                '<:happy_mention_9:1409479943351701514>',
                '<:happy_mention_10:1409479963618316338>',
                '<:happy_mention_11:1409479982446542868>',
                '<:happy_mention_12:1409480002902298744>',
                '<:happy_mention_13:1409480021336391873>',
                '<:happy_mention_14:1409480042257584239>',
                '<:happy_mention_15:1409480610174730323>',
                '<:happy_mention_16:1409480633641861160>',
                '<:happy_mention_17:1409480653434781736>',
                '<:happy_mention_18:1409480673366118463>',
                '<:happy_mention_19:1409480697269452933>',
                '<:happy_mention_20:1409480716638490715>',
            ]
        elif interaction.command.name == 'angrymention':
            emojis = [
                '<:angry_mention_1:1409480828043661412>',
                '<:angry_mention_2:1409480931630256180>',
                '<:angry_mention_3:1409480949581742142>',
                '<:angry_mention_4:1409480967957118996>',
                '<:angry_mention_5:1409481020188659773>',
                '<:angry_mention_6:1409481044540919819>',
                '<:angry_mention_7:1409481064036044980>',
                '<:angry_mention_8:1409481087419285514>',
                '<:angry_mention_9:1409481106432200725>',
                '<:angry_mention_10:1409481124408983614>',
                '<:angry_mention_11:1409481142528376975>',
                '<:angry_mention_12:1409481160005914785>',
                '<:angry_mention_13:1409481177617797180>',
                '<:angry_mention_14:1409481208664166471>',
                '<:angry_mention_15:1409481231569129563>',
                '<:angry_mention_16:1409481254738333827>',
                '<:angry_mention_17:1409481273994383421>',
                '<:angry_mention_18:1409481293745492008>',
                '<:angry_mention_19:1409481315912515644>',
                '<:angry_mention_20:1409481764656648324>',
            ]

        await interaction.edit_original_response(content=emojis[0])

        await message.reply(content=f'-# {interaction.user.mention} 加了一大堆 {emojis[0]}', mention_author=False)

        for emoji in emojis:
            try:
                await message.add_reaction(emoji)
            except Exception as e:
                await interaction.edit_original_response(content=str(e))
                break

async def setup(bot):
    await bot.add_cog(Emoji(bot))
