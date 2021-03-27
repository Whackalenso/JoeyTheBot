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

    async def deleteMaybe(self, _message, _history):
        content = _message.content.replace('\n', '')
        if (content.isnumeric()):
            try:
                prevMsg = _history[1]
                prev = int(prevMsg.content)
            except:
                return

            if (prevMsg.author.id != _message.author.id) & (int(content)-1 == prev):
                return

        await _message.delete()

    @commands.Cog.listener()
    async def on_message(self, message):
        if not await self.cog_check(message.guild):
            return

        chan = message.channel
        if (chan.id == 775803582720639017):
            history = await chan.history(limit=2).flatten()
            await self.deleteMaybe(message, history)

    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload):
        channel = self.bot.get_channel(payload.channel_id)
        if channel.id != 775803582720639017:
            return

        message = await channel.fetch_message(payload.message_id)

        hist = await channel.history(limit=2).flatten()
        if message != hist[0]:
            return

        await self.deleteMaybe(message, hist)

def setup(bot):
    bot.add_cog(CountingChannel(bot))