import discord
from discord.ext import commands
from typing import Union
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta
import time
import json

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
    async def statistics(self, ctx, *, timeFrame:Union[str, None]):
        importantChannels = [
            755021484686180437, #general
            758871523799990292, #images
            755133977173426312, #welcome-verify
            755157589154594876, #questions
            776499496543715379, #gifs
            773401331321929748, #politics
            755615740568272958, #music
            756192693910110208, #memes
            778018663478722581, #books
            773383060653604874, #reddit
            774141838218100756, #the-twilight-zone
            755980167356219403, #gaming
            755522123308728411  #bot-commands
        ]
        messageAmounts = {}

        if (timeFrame.lower() == 'today'):
            subtract = 86400
            if (datetime.now().hour > 8):
                subtract *= 2
            yesterday = datetime.utcfromtimestamp(time.time() - subtract) #utc
            today = datetime.now().date() #local
            for _id in importantChannels:
                channel = self.bot.get_channel(_id)
                history = await channel.history(limit=None, after=yesterday).flatten()
                messagesByHour = {}
                for m in history:
                    createdAt = m.created_at - timedelta(hours=8)
                    if (createdAt.date() == today):
                        hour = createdAt.hour
                        if (messagesByHour.get(hour)):
                            messagesByHour[hour] += 1
                        else:
                            messagesByHour[hour] = 1
                messageAmounts[_id] = messagesByHour
            with open('test.json', 'w') as f:
                json.dump(messageAmounts, f, indent=4)
            await ctx.send("The data has been printed to the console.")

            # embed = discord.Embed(
            #     title="Server Analytics for today",
            #     color=discord.Color.blue()
            # )

        # plt.plot([1, 2], [1, 2])
        # plt.savefig('graph.png')
        # plt.close()
        # with open('graph.png', 'rb') as f:
        #     graph = discord.File(f)
        #     await ctx.send(file=graph)
    
def setup(bot):
    bot.add_cog(Analytics(bot))