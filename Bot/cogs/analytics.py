import discord
from discord.ext import commands
from typing import Union
import matplotlib.pyplot as plt

#today--
#total messages sent
#bar graph showing the amount of messages sent for each hour of the day and each important channel

#this week--
#total messages sent
#bar graph showing the amount of messages sent for each day
#pie graph showing most popular channel
#pie graph showing post popular time of day

#this month--
#total messages sent
#bar graph showing the amount of messages sent for each week
#pie graph showing most popular channel
#pie graph showing post popular time of day

#forever--
#total messages sent
#graph showing the amount of messages sent each week over time
#pie graph showing most popular channel
#pie graph showing post popular time of day

class Analytics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def statistics(self, ctx): #, *, _timeFrame=Union[str, None]
        plt.plot([1, 2], [1, 2])
        plt.savefig('graph.png')
        plt.close()
        with open('graph.png', 'rb') as f:
            graph = discord.File(f)
            await ctx.send(file=graph)
    
def setup(bot):
    bot.add_cog(Analytics(bot))