import discord
from discord.ext import commands
from typing import Union
import matplotlib.pyplot as plt
import numpy as np
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
        importantChannels = {
            'general': 755021484686180437,
            'images': 758871523799990292,
            'gifs': 776499496543715379,
            'politics': 773401331321929748,
            'music': 755615740568272958,
            'memes': 756192693910110208,
            'books': 778018663478722581,
            'reddit': 773383060653604874,
            'the-twilight-zone': 774141838218100756,
            'gaming': 755980167356219403,
            'bot-commands': 755522123308728411,
            'welcome-verify': 755133977173426312,
            'questions': 755157589154594876,
        }
        messageAmounts = {}

        if (timeFrame.lower() == 'today'):
            #getting data
            totalMessages = []
            subtract = 86400
            if (datetime.now().hour > 8):
                subtract *= 2
            yesterday = datetime.utcfromtimestamp(time.time() - subtract) #utc
            today = datetime.now().date() #local
            for _name, _id in importantChannels.items():
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
                        totalMessages.append(m)
                messageAmounts[_name] = messagesByHour
            with open('test.json', 'w') as f:
                json.dump(messageAmounts, f, indent=4)

            #member data
            memberMsgs = {}
            for m in totalMessages:
                if (not m.author.bot):
                    auth = m.author.display_name
                    if (memberMsgs.get(auth)):
                        memberMsgs[auth] += 1
                    else:
                        memberMsgs[auth] = 1

            top3Membs = []
            while len(top3Membs) < 3:
                topMemb = ''
                for a, n in memberMsgs.items(): #author, number
                    if (a not in top3Membs):
                        if (topMemb == ''):
                            topMemb = a
                            continue

                        _top = topMemb if isinstance(topMemb, str) else topMemb[0]
                        if (n > memberMsgs[_top]):
                            topMemb = a

                        if (n == memberMsgs[_top]):
                            if (isinstance(topMemb, list)):
                                topMemb.append(a)
                            else:
                                topMemb = [a, topMemb]
                        
                top3Membs.append(topMemb)

            #making graph
            plt.figure(figsize=(20,5))
            N = 24
            ind = np.arange(N)
            width = 1/len(importantChannels)
            times = [str(i) for i in range(24)] #excludes 24
            iteration = 0
            for _name, _dict in messageAmounts.items():
                #Example: plt.bar(ind, men_means, width, label='Men')
                values = []
                for _hour, _num in _dict.items():
                    while _hour - len(values) >= 1:
                        values.append(0)
                    values.append(_num)
                for _ in range(24 - len(values)):
                    values.append(0)

                plt.bar(ind + (width * iteration), tuple(values), width, label=_name)
                iteration += 1

            plt.ylabel('Messages')
            plt.xlabel('Hours')
            plt.xticks(ind + width, tuple(times)) # / 2
            plt.legend(loc='best')
            plt.savefig('graph.png', bbox_inches = 'tight')
            plt.close()

            #sending graph
            memberStr = '\n`#{}` {} | {} messages | {:.0%} of activity'
            top3Str = ''
            for i in range(len(top3Membs)):
                name = top3Membs[i]
                if (isinstance(name, list)):
                    msgs = memberMsgs[name[0]]
                    name = ' & '.join(name)
                else:
                    msgs = memberMsgs[name]
                top3Str = top3Str + memberStr.format(i + 1, name, msgs, msgs/len(totalMessages))

            embed = discord.Embed(
                title="Server Analytics for today",
                description=f'**Total messages:** {len(totalMessages)}\n**Top 3 members:**{top3Str}',
                color=discord.Color.blue()
            )
            _file = discord.File("./graph.png", filename="graph.png")
            embed.set_image(url="attachment://graph.png")
            embed.set_footer(text='Click the image to make it bigger.')
            await ctx.send(file=_file, embed=embed)
            

        # plt.plot([1, 2], [1, 2])
        # plt.savefig('graph.png')
        # plt.close()
        # with open('graph.png', 'rb') as f:
        #     graph = discord.File(f)
        #     await ctx.send(file=graph)
    
def setup(bot):
    bot.add_cog(Analytics(bot))