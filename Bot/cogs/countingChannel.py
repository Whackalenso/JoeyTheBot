import discord
from discord.ext import commands

class CountingChannel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.servers = [755021484686180432]

    async def cog_check(self, ctx):
        if isinstance(ctx, commands.Context):
            return ctx.guild.id in self.servers
        elif ctx == None:
            return True
        else:
            return ctx.id in self.servers

    @commands.Cog.listener()
    async def on_message(self, message):
        if not await self.cog_check(message.guild):
            return

        chan = message.channel
        if (chan.id == 775803582720639017):
            if (message.content.isnumeric()):
                history = await chan.history(limit=2).flatten()
                try:
                    prevMsg = history[1]
                    prev = int(prevMsg.content)
                except:
                    return

                if (prevMsg.author.id != message.author.id) & (int(message.content)-1 == prev):
                    return

            await message.delete()

    # @commands.Cog.listener()
    # async def on_raw_message_edit(self, payload):
        


def setup(bot):
    bot.add_cog(CountingChannel(bot))