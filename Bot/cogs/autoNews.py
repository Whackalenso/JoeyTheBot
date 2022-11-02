import discord
from discord.ext import commands, tasks
from bs4 import BeautifulSoup
import requests
import os
import math

class AutoNews(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.newsLoop.start() # pylint: disable=no-member

    def updateData(self, data):
        for c in os.listdir(f'Bot/cogs'):
            if ('AutoNews' != c.capitalize()):
                cog = self.bot.get_cog(c.capitalize())
                if (cog != None):
                    cog.bot.botData = data

    #Command to set the News Channel
    @commands.command()
    async def setNewsChannel(self, ctx, channel:discord.TextChannel):
        self.bot.botData['newsData']['channel'] = channel.id
        self.updateData(self.bot.botData)
        await self.bot.database.save_data(self.bot.botData)
        await ctx.send(f"News channel set to {channel.mention}")

        if not self.newsLoop.is_running(): # pylint: disable=no-member
            self.newsLoop.start() # pylint: disable=no-member

    @tasks.loop(minutes=10)
    async def newsLoop(self):
        #Scrape BBC and extract the headlines
        URL = requests.get("https://www.bbc.co.uk/news")
        soup = BeautifulSoup(URL.text, 'html.parser')
        heads = soup.select(".gs-c-promo-heading__title")

        linksToSend = []
        alreadySent = self.bot.botData['newsData']['headlines']
        for i in range(10):
            link = 'https://www.bbc.com' + heads[i].parent.get('href')
            if link not in alreadySent:
                linksToSend.append(link)
                alreadySent.append(link)

        if linksToSend != []:
            channelId = self.bot.botData['newsData']['channel']
            channel = self.bot.get_guild(755021484686180432).get_channel(channelId)

            linksToSend = [linksToSend[i:i+5] for i in range(0,len(linksToSend),5)] #do this cuz of embed limit
            for l in linksToSend:
                await channel.send('\n'.join(l))

            self.bot.botData['newsData']['headlines'] = alreadySent
            self.updateData(self.bot.botData)
            await self.bot.database.save_data(self.bot.botData)
        
    @newsLoop.before_loop
    async def news_before_loop(self):
        #dont need to wait till ready cuz it starts in the ready funct
        if self.bot.botData['newsData']['channel'] == None:
            self.newsLoop.stop() # pylint: disable=no-member

def setup(bot):
    bot.add_cog(AutoNews(bot))