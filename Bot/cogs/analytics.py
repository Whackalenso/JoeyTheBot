import discord
from discord.ext import commands
from typing import Union
import matplotlib.pyplot as plt

class Analytics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def statistics(self, ctx): #, *, _timeFrame=Union[str, None]
        plt.plot([1, 2], [1, 2]) #this is just a test
        plt.savefig('graph.png')
        plt.close()
        with open('graph.png', 'rb') as f:
            file=discord.File(f)
            await ctx.send(file=file)
    
def setup(bot):
    bot.add_cog(Analytics(bot))