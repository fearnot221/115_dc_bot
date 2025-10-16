import discord
from discord.ext import commands

msg_history: dict[int, list[discord.Message]] = {}

class Event(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot: return

        if message.channel.id not in msg_history: msg_history[message.channel.id] = []
        if msg_history[message.channel.id]:
            if msg_history[message.channel.id][-1].content == message.content and message.author not in (msg.author for msg in msg_history[message.channel.id]):
                msg_history[message.channel.id].append(message)
            else:
                data = msg_history.pop(message.channel.id)

                if len(data) >= 3:
                    emoji = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']
                    if len(data) <= 9:
                        await message.add_reaction(emoji[len(data)])
                    else:
                        num_str = str(len(data))
                        for digit in num_str:
                            await message.add_reaction(emoji[int(digit)])
        else:
            msg_history[message.channel.id].append(message)

async def setup(bot):
    await bot.add_cog(Event(bot))