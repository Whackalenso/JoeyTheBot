import discord
from discord.ext import commands
from discord.utils import get
import asyncio
import time
import os

class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.acceptMsgId = 758486195985973269
        self.userAcceptTimes = {}
        
        #if cogs got loaded before the bot runs, put this in an on_ready
        self.welcome_verify = self.bot.get_channel(755133977173426312)
        self.modVerify = self.bot.get_channel(758376336984899596)
        self.termsChannel = self.bot.get_channel(755133859682713741)
        
        guild = self.bot.get_guild(755021484686180432)
        self.peopleRole = get(guild.roles, id=755135494677070005)
        self.getsPingedToVerifyPeopleRole = get(guild.roles, id=758120042520248331)
        self.notVerifiedRole = get(guild.roles, id=755146208623984741)
        self.botRole = get(guild.roles, id=755137354888511498)

    def updateData(self, data):
        for c in os.listdir(f'{self.bot.mainFolder}/Bot/cogs'):
            if ('Verification' != c.capitalize()):
                cog = self.bot.get_cog(c.capitalize())
                if (cog != None):
                    cog.bot.botData = data

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if (member.bot):
            await asyncio.sleep(5)
            await member.remove_roles(self.notVerifiedRole)
            await member.add_roles(self.botRole)

    @commands.Cog.listener()
    async def on_member_update(self, before, after): # this is for getting roles instead of .setschedule
        if ((self.notVerifiedRole in after.roles) & (before.roles != after.roles) & (not self._schoolRoleCheck(before))):
            isUserReady = await self._isUserReady(after)
            if (isUserReady):
                await self._userIsReady(after)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload): #on_reaction_add(reaction, user:discord.Member)
        checkEmoji = '✅'
        user = payload.member
        if ((user.bot == False) if user != None else False):

            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)

            if (message.id == self.acceptMsgId):
                if (payload.emoji.name != checkEmoji):
                    await message.clear_reaction(payload.emoji) #reaction.clear()
                else:
                    #await _userAccept(user)
                    if (self.notVerifiedRole in user.roles):
                        if ((time.time() - self.userAcceptTimes[user.id] >= 120) if self.userAcceptTimes.get(user.id) != None else True): # 2 mins
                            if (user.nick != None): name = user.nick
                            else: name = user.name
                            await self.welcome_verify.send(f"**{name}** has accepted the terms.")
                            self.userAcceptTimes[user.id] = time.time()
                        isUserReady = await self._isUserReady(user)
                        if (isUserReady):
                            await self._userIsReady(user)

            #-----

            reactionForVerification = False
            userForVerificationMsg = ''
            for member, msgId in self.bot.botData['verifyMsgs'].items():
                if (message.id == msgId):
                    userForVerificationMsg = get(channel.guild.members, id=int(member)) #member (before, members were discord.Member, but now I'm changing them to discord.Member.id)
                    reactionForVerification = True
                    self.bot.botData['verifyMsgs'].pop(member)
                    self.updateData(self.bot.botData)
                    break

            if (reactionForVerification == True):
                if (payload.emoji.name != checkEmoji):
                    await message.clear_reaction(payload.emoji)
                else:
                    await message.delete()
                    await userForVerificationMsg.remove_roles(self.notVerifiedRole)
                    await userForVerificationMsg.add_roles(self.peopleRole)
                    #await putScheduleInChannel(userForVerificationMsg, bot.botData['schedules'][str(userForVerificationMsg.id)]) #bot.schedules[userForVerificationMsg.id]
                    await self.welcome_verify.send(f"**{userForVerificationMsg.mention}** is now verified.")
                    # bot.botData['schedules'].pop(str(userForVerificationMsg.id))
                    # await bot.database.save_data(bot.botData)

    def _schoolRoleCheck(self, member:discord.Member):
        subjects = ['english', 'history', 'math', 'PE', 'science'] # for now don't do elective
        electives = ['Band', 'Art', 'Gateway', 'Spanish']
        takenSubjects = []
        gradeTaken = False
        electiveTaken = False
        for r in member.roles:
            for s in subjects:
                if (r.name.endswith(f" - {s}")):
                    takenSubjects.append(s)
                if ('grade' in r.name.lower()):
                    gradeTaken = True
            for e in electives:
                if (r.name == e):
                    electiveTaken = True
                    break
        if ((all([s in takenSubjects for s in subjects])) & (gradeTaken) & (electiveTaken)):
            return True
        if (get(member.roles, id=773395171420667923) != None): #not student
            return True
        
        return False

    @commands.command()
    async def verify(self, ctx, *, member:discord.Member):
        if (ctx.message.author.guild_permissions.administrator):
            if (member.bot == False):
                if (self.notVerifiedRole in member.roles):
                    isUserReady = await self._isUserReady(member)
                    if (isUserReady):
                        await member.remove_roles(self.notVerifiedRole)
                        await member.add_roles(self.peopleRole)
                        #await putScheduleInChannel(member, bot.botData['schedules'][str(member.id)]) #bot.schedules[member.id]
                        await ctx.send(f"**{member.nick}** is now verified.")
                        #self.bot.botData['schedules'].pop(str(member.id))
                        #await self.bot.database.save_data(self.bot.botData)

                    usersAccepted = await self._getUsersAccepted()
                    if (member not in usersAccepted):
                        await ctx.send("This person has not accepted the terms of agreement.")
                    if (member.nick == None):
                        await ctx.send("This person has not set their name.")
                    #if (str(member.id) not in self.bot.botData['schedules']):
                        #await ctx.send("This person has not set their schedule. If this person isn't a student, they can just say **.setSchedule not student**.")
                else:
                    await ctx.send("This person is already verified.")
            else:
                await ctx.send("You can't verify a bot.")
        else:
            await ctx.send("You need admin perms to do this")

    async def _isUserReady(self, user:discord.Member):
        usersAccepted = await self._getUsersAccepted()
        if ((user in usersAccepted) & (user.nick != None) & (self._schoolRoleCheck(user))): # (str(user.id) in bot.botData['schedules']) & 
            return True

        return False

    async def _userIsReady(self, user:discord.Member):
        #if (bot.botData['verifyMsgs'].get(str(user.id)) == None):
        await self.welcome_verify.send(f"**{user.name} is now ready to be verified.** A mod or founder will verify you soon.")

        embed = discord.Embed(
            title=f"Verify {user.nick}?",
            color=discord.Color.gold()
        )
        msg = await self.modVerify.send(content=f"{self.getsPingedToVerifyPeopleRole.mention}", embed=embed)
        await msg.add_reaction("✅")
        self.bot.botData['verifyMsgs'][str(user.id)] = msg.id
        self.updateData(self.bot.botData)
        await self.bot.database.save_data(self.bot.botData)

    @commands.command()
    async def setName(self, ctx, *, _name):
        if (self.notVerifiedRole in ctx.author.roles):
            if (ctx.message.channel == self.welcome_verify):
                words = _name.split(' ')
                if (len(words) >= 2):
                    for i in range(len(words)):
                        words[i] = words[i].capitalize()
                    name = ' '.join(words)

                    await ctx.author.edit(nick=name)
                    await ctx.send("Your name has been set")

                    if (self.notVerifiedRole in ctx.author.roles):
                        isUserReady = await self._isUserReady(ctx.author)
                        if (isUserReady):
                            await self._userIsReady(ctx.author)

                else:
                    await ctx.send("Make sure you put your first and last name.")
            else:
                msg = await ctx.send(f"Do this in {self.welcome_verify.mention} please.")
                time.sleep(5)
                await ctx.message.delete()
                await msg.delete()
        else:
            await ctx.send("You're already verified so you can't use this command.")

    # async def putScheduleInChannel(user:discord.Member, periods):
    # 	embed = discord.Embed(
    # 		title = f"{user.nick}'s Schedule",
    # 		color = discord.Color.blue()
    # 	)
    # 	embed.add_field(name=periods[0], value="Homeroom", inline=False)

    # 	numberPeriods = periods.copy()
    # 	numberPeriods.pop(0)
    # 	if (len(periods) == 8):
    # 		numberPeriods.pop(-1)
    # 	nums = ['1', '2', '3', '4/5', '6', '7']

    # 	for i in range(len(numberPeriods)):
    # 		embed.add_field(name=numberPeriods[i], value=f"Period {nums[i]}", inline=False)

    # 	if (len(periods) == 8):
    # 		embed.add_field(name=periods[-1], value="Extra", inline=False)

    # 	await bot.schedulesChannel.send(embed=embed)

    async def _getUsersAccepted(self):
        msg = await self.termsChannel.fetch_message(self.acceptMsgId)
        for reaction in msg.reactions:
            if (reaction.emoji == '✅'):
                users = await reaction.users().flatten()
                return users

def setup(bot):
    bot.add_cog(Verification(bot))