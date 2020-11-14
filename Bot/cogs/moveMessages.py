import discord
from discord.ext import commands
from discord.utils import get
from typing import Union
import io

class MoveMessages(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def getMessagesFromRange(self, history, id1:int, id2:int):
        msgs = []
        inRange = False
        async for m in history:
            if (m.id == id1):
                inRange = True

            if (inRange == True):
                msgs.append(m)

            if (m.id == id2):
                break
        
        msgs.reverse()
        return msgs

    async def moveMessageHelper(self, ctx, newChannel, msg):
        me = ctx.guild.me
        botNick = me.nick
        msgAuthor = get(ctx.guild.members, id=msg.author.id)

        files = []
        for att in msg.attachments:
            files.append(f"{att.url}")
        
        await me.edit(nick=msgAuthor.nick)
        if ((msg.content != None) & (msg.content != '')):
            await newChannel.send(msg.content, allowed_mentions=discord.AllowedMentions.none())
        for f in files:
            await newChannel.send(f)
        await me.edit(nick=botNick)

        strUser = msgAuthor
        if (strUser.nick != None):
            strUser = strUser.nick

        await msg.delete()
        await ctx.message.delete()
        await ctx.send(f"**{strUser}**'s message has been moved to {newChannel.mention}")

    async def moveMessagesHelper(self, ctx, newChannel, msgs):
        changeNick = all(m.author == msgs[0].author for m in msgs)
        if (changeNick):
            me = ctx.guild.me
            botNick = me.nick
            msgAuthor = get(ctx.guild.members, id=msgs[0].author.id)
            if (msgAuthor.nick != None):
                await me.edit(nick=msgAuthor.nick)
            else:
                await me.edit(nick=msgAuthor.display_name)

        previousAuthor = ''
        avatars = {}
        for msg in msgs:

            files = []
            for att in msg.attachments:
                files.append(f"{att.url}")

            if ((changeNick == False) & (previousAuthor != msg.author)):
                
                avatarEmoji = ''
                if (msg.author.id not in avatars.keys()):
                    avatarFile = io.BytesIO()
                    await msg.author.avatar_url_as(size=32).save(avatarFile, seek_begin=True)
                    data = io.BytesIO(avatarFile.getvalue())

                    avatarEmoji = await ctx.guild.create_custom_emoji(name=f"pfp_{msg.author.id}", image=data.read()) #indent
                    avatars[msg.author.id] = avatarEmoji
                    
                else:
                    avatarEmoji = avatars[msg.author.id]

                strUser = msg.author
                if (strUser.nick != None):
                    strUser = strUser.nick

                animated = ''
                if (avatarEmoji.animated):
                    animated = 'a'
                header = f"<{animated}:{avatarEmoji.name}:{avatarEmoji.id}> **{strUser}:**\n** **" #maybe add the date idk
                if (previousAuthor != ''):
                    header = f"** **\n{header}"
                await newChannel.send(header)
                previousAuthor = msg.author
            
            if ((msg.content != None) & (msg.content != '')):
                await newChannel.send(msg.content, allowed_mentions=discord.AllowedMentions.none())
            for f in files:
                await newChannel.send(f)

            await msg.delete()
        
        if (changeNick): await me.edit(nick=botNick)
        for e in avatars.values():
            await e.delete()
        await ctx.message.delete()
        await ctx.send(f"**{len(msgs)}** messages have been moved to {newChannel.mention}")

    @commands.command()
    async def moveMessages(self, ctx, _range, newChannel:discord.TextChannel):
        if (ctx.author.guild_permissions.administrator):
            if (ctx.channel.id != newChannel.id):
                async with ctx.typing():

                    msgs = None
                    idList = _range.lower().split('-')
                    history = await ctx.channel.history(limit=5).flatten()
                    if ((len(history) > 1) == False):
                        await ctx.send("There's no messages in this channel yet.")
                        return

                    if (len(idList) == 2):
                        if (all(i.isnumeric() for i in idList)):
                            msgs = await self.getMessagesFromRange(ctx.channel.history(), int(idList[0]), int(idList[1]))
                        elif ((idList[0] == 'recent') & (idList[1].isnumeric())):
                            msgs = await self.getMessagesFromRange(ctx.channel.history(), history[1].id, int(idList[1]))
                        else:
                            await ctx.send(f"I don't know what you mean by **{_range}**.")
                    else:
                        await ctx.send(f"I don't know what you mean by **{_range}**.")

                    if (msgs != None):
                        await self.moveMessagesHelper(ctx, newChannel, msgs)
                    else:
                        print("An error has occured. Contact <@545020858113196053>.")

            else:
                await ctx.send("That's the same channel that you're currently in. Make sure to do a different one.")
        else:
            await ctx.send("You need admin perms to do this.")

    @commands.command()
    async def moveMessage(self, ctx, id:Union[int, str], newChannel:discord.TextChannel):
        if (ctx.author.guild_permissions.administrator):
            if (ctx.channel.id != newChannel.id):
                async with ctx.typing():

                    msg = None
                    if (isinstance(id, int)):
                        msg = await ctx.channel.fetch_message(id)
                        if (msg == None):
                            await ctx.send("Either this id is wrong, or the message doesn't exist in this channel. (Use this command in the channel the message exists in)")
                            return
                    elif (isinstance(id, str)):
                        history = await ctx.channel.history(limit=5).flatten()
                        if ((len(history) > 1) == False):
                            await ctx.send("There's no messages in this channel yet.")
                            return

                        if (id.lower() == 'recent'):
                            msg = history[1]
                        else:
                            await ctx.send(f"I don't know what you mean by **{id}**.")

                    if (msg != None):
                        await self.moveMessageHelper(ctx, newChannel, msg)
                    else:
                        print("An error has occured. Contact <@545020858113196053>.")

            else:
                await ctx.send("That's the same channel that you're currently in. Make sure to do a different one.")
        else:
            await ctx.send("You need admin perms to do this.")

def setup(bot):
    bot.add_cog(MoveMessages(bot))