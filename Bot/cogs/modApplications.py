import discord
from discord.ext import commands
from discord.utils import get
import os

class ModApplications(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.anonymousExtraFooter = " React with ✅ to reveal who this person is. Do .talk <id of this message> <message> to communicate with this person while keeping it anonymous."
        self.userApplicationData = {}
        self.applicationQuestions = self.bot.botData['applicationData']['questions']

        self.servers = [755021484686180432]

    async def cog_check(self, ctx):
        if isinstance(ctx, commands.Context):
            return ctx.guild.id in self.servers
        else:
            return ctx.id in self.servers

    def updateData(self, data):
        for c in os.listdir(f'{self.bot.mainFolder}/Bot/cogs'):
            if ('ModApplications' != c.capitalize()):
                cog = self.bot.get_cog(c.capitalize())
                if (cog != None):
                    cog.bot.botData = data

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if not await self.cog_check(before.guild):
            return

        modRole = get(after.guild.roles, id=755208276022657085)
        if ((self.bot.botData['applicationData']['userApplicationData'].get(str(after.id)) != None) & (modRole in after.roles) & (after.roles != before.roles)):
            await self._giveMod(after)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload): #on_reaction_add(reaction, user:discord.Member)
        if not await self.cog_check(self.bot.get_guild(payload.guild_id)):
            return
            
        checkEmoji = '✅'
        user = payload.member
        if ((user.bot == False) if user != None else False):

            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)

            if ((str(message.id) in self.bot.botData['applicationData']['modMsgs']) & (payload.emoji.name == checkEmoji)):
                await self._reveal(message)

        elif (payload.user_id != self.bot.user.id):
            user = self.bot.get_user(payload.user_id)
            if (not user.bot):
                if (user.dm_channel == None):
                    try:
                        await user.create_dm()
                        message = await user.dm_channel.fetch_message(payload.message_id)
                    except discord.errors.HTTPException as e:
                        print(e)
                
            questions = self.bot.botData['applicationData']['userApplicationData'][str(payload.user_id)].get('modQuestions')
            if (questions != None):
                qEmbed = message.embeds[0].to_dict()
                if ((payload.emoji.name == '💬') & (qEmbed in questions)):
                    await self._respond(payload.user_id, qEmbed)
                    return

    @commands.Cog.listener()
    async def on_message(self, message):
        # I dont do a check for this one because the message guild should be none anyways

        if (message.guild == None):
            data = self.bot.botData['applicationData']['userApplicationData'].get(str(message.author.id))
            if (data != None):
                if (message.content == '[restart]'):
                    await self._startApplication(message.author)
                    return

                if (message.content == '[cancel]'):
                    await self._cancelApplication(message.author)
                    return

                if (data.get('sessionActive')):
                    if (data['questionsAsked'] < len(self.applicationQuestions)):
                        q = self.applicationQuestions[data['questionsAsked']]
                        await message.author.send(f"**Question {data['questionsAsked'] + 1} of {len(self.applicationQuestions)}:** " + q)
                        data['questionsAsked'] += 1
                    elif (data['questionsAsked'] == len(self.applicationQuestions)):
                        await self._applicationComplete(message.author)

                    #bot.botData['applicationData']['userApplicationData'] = bot.userApplicationData
                    self.bot.botData['applicationData']['userApplicationData'][str(message.author.id)] = data
                    self.updateData(self.bot.botData)
                    await self.bot.database.save_data(self.bot.botData)

                elif (data.get('activeQuestionSession') != None):
                    await self._userHasResponded(message.author, message.content, data['activeQuestionSession'])

    @commands.command()
    async def apply(self, ctx):
        userData = self.bot.botData['applicationData']['userApplicationData'].get(str(ctx.author.id))
        if (userData['sessionActive'] if userData != None else False): #check if none
            await ctx.send("You're already in the process of forming your application.")
            return
        await ctx.message.delete()

        anonymousApplications = self.bot.botData['applicationData']['anonymousApplications']
        infoMsg = 'Type [restart] to start over.'
        if (anonymousApplications):
            infoMsg = infoMsg + " (Btw this is supposed to be an anonymous application, so don't say anything relating to who you are.)"
        await self._startApplication(ctx.author)

    async def _startApplication(self, user):
        await user.send("`Type [restart] to restart and [cancel] to cancel.`")
        await user.send(f"**Question 1 of {len(self.applicationQuestions)}:** " + self.applicationQuestions[0])
        userData = self.userApplicationData.get(str(user.id))
        if (userData != None):
            self.userApplicationData[str(user.id)].update({'questionsAsked': 1, 'sessionActive': True})
        else:
            self.userApplicationData[str(user.id)] = {'questionsAsked': 1, 'sessionActive': True}
        self.bot.botData['applicationData']['userApplicationData'] = self.userApplicationData
        await self.bot.database.save_data(self.bot.botData)

    async def _applicationComplete(self, _user):
        guild = self.bot.get_guild(755021484686180432) # korematsu server
        member = guild.get_member(_user.id)
        modMsgChannel = guild.get_channel(773787257480019979)
        updating = self.bot.botData['applicationData']['userApplicationData'][str(_user.id)].get('modMsg') != None
        msg = await _user.send(f"You're application has been {'updated' if updating else 'complete'}. You will be notified if a founder accepts this application.")

        messages = await msg.channel.history().flatten()

        answers = [] #this might be a more sensible solution
        for m in messages:
            if (m.author.id == _user.id):
                answers.append(m.content)
                if (len(answers) == len(self.applicationQuestions)):
                    break
        answers.reverse()
        # amountOfMsgsToInclude = (len(bot.applicationQuestions) * 2) + 1
        # amountOfMsgsToExclude = len(messages) - amountOfMsgsToInclude
        # for i in range(amountOfMsgsToExclude):
        # 	messages.pop(-1)
        # messages.reverse()

        # answers = []
        # for m in messages:
        # 	if (m.author.id == _user.id):
        # 		answers.append(m.content)

        if (not updating):
            embed = discord.Embed(
                color=discord.Color.green()
            )
            anonymousApplications = self.bot.botData['applicationData']['anonymousApplications']
            if (anonymousApplications):
                embed.set_author(name="Anonymous User")
            else: # do something about contacting them if they're anonymous
                embed.set_author(name=member.display_name, icon_url=str(_user.avatar_url))
            
            embed.set_footer(text=f"React with 👍 or 👎 to vote on whether this person should become mod.{self.anonymousExtraFooter if anonymousApplications else ''}")
            for q in range(len(self.applicationQuestions)):
                embed.add_field(name=self.applicationQuestions[q], value=answers[q])
            
            founderRole = get(self.bot.get_guild(755021484686180432).roles, id=755131725721370636)
            msg = await modMsgChannel.send(content=f"{founderRole.mention}", embed=embed)
            self.bot.botData['applicationData']['modMsgs'][str(msg.id)] = _user.id
            self.bot.botData['applicationData']['userApplicationData'][str(_user.id)]['modMsg'] = msg.id

            await msg.add_reaction('👍')
            await msg.add_reaction('👎')
            if (anonymousApplications): 
                await msg.add_reaction('✅')
            await msg.pin()
        else:
            msg = await modMsgChannel.fetch_message(self.bot.botData['applicationData']['userApplicationData'][str(_user.id)]['modMsg'])
            embed = msg.embeds[0]
            embed.clear_fields()
            for q in range(len(self.applicationQuestions)):
                embed.add_field(name=self.applicationQuestions[q], value=answers[q])
            await msg.edit(embed=embed)

            
            alert_embed = discord.Embed(
                title="Update Alert",
                description=f"The application at [this link]({msg.jump_url}) was updated.",
                color=discord.Color.blue()
            )
            await modMsgChannel.send(embed=alert_embed)

        userData = self.bot.botData['applicationData']['userApplicationData'][str(_user.id)]
        userData['sessionActive'] = False
        userData.pop('questionsAsked')

        if (userData.get('queuedQuestions') != None):
            for e in userData['queuedQuestions']:
                embed = discord.Embed.from_dict(e)
                await self._askQuestion(embed, _user)
                userData['queuedQuestions'].remove(e)

        self.bot.botData['applicationData']['userApplicationData'][str(_user.id)] = userData
        await self.bot.database.save_data(self.bot.botData)

    async def _giveMod(self, member):
        guild = self.bot.get_guild(755021484686180432) # korematsu server
        generalChannel = guild.get_channel(755021484686180437)
        modAppChannel = guild.get_channel(773787257480019979)
        msgId = self.bot.botData['applicationData']['userApplicationData'][str(member.id)]['modMsg']
        msg = await modAppChannel.fetch_message(msgId)

        await generalChannel.send(f"{member.mention} has been granted mod! \*clapping*")
        await msg.delete()
        self.bot.botData['applicationData']['userApplicationData'].pop(str(member.id))
        await self.bot.database.save_data(self.bot.botData)

    async def _reveal(self, msg):
        guild = self.bot.get_guild(755021484686180432) # korematsu server
        memberId = self.bot.botData['applicationData']['modMsgs'][str(msg.id)]
        member = get(guild.members, id=memberId)

        embed = msg.embeds[0]
        embed.set_author(name=member.display_name, icon_url=str(member.avatar_url))
        embed.set_footer(text=embed.footer.text.replace(self.anonymousExtraFooter, ''))
        await msg.edit(embed=embed)
        await msg.clear_reaction('✅')
        
    @commands.command()
    async def toggleAnonymousApplications(self, ctx):
        self.bot.botData['applicationData']['anonymousApplications'] = not self.bot.botData['applicationData']['anonymousApplications']
        await ctx.send(f"This is now set to {self.bot.botData['applicationData']['anonymousApplications']}.")
        await self.bot.database.save_data(self.bot.botData)

    @commands.command()
    async def setQuestions(self, ctx, *, _questions):
        self.applicationQuestions = [q.strip(' ') for q in _questions.split('|')]
        self.bot.botData['applicationData']['questions'] = self.applicationQuestions
        await ctx.send("The questions have been updated.")
        await self.bot.database.save_data(self.bot.botData)

    @commands.command()
    async def talk(self, ctx, msgId, *, message):
        if (ctx.author.guild_permissions.administrator):
            userId = self.bot.botData['applicationData']['modMsgs'][str(msgId)]
            user = get(ctx.guild.members, id=userId)
            
            embed = discord.Embed(
                title="An admin has asked you a question regarding your application.",
                description=message,
                color=discord.Color.blue()
            )
            embed.set_footer(text="React with 💬 at any time to respond back. We communicate this way to keep things anonymous.")
            userData = self.bot.botData['applicationData']['userApplicationData'][str(userId)]
            if (userData.get('sessionActive') or userData.get('activeQuestionSession') != None):
                queuedQuestions = self.bot.botData['applicationData']['userApplicationData'][str(userId)].get('queuedQuestions')
                if (queuedQuestions != None):
                    self.bot.botData['applicationData']['userApplicationData'][str(userId)]['queuedQuestions'].append(embed.to_dict())
                else:
                    self.bot.botData['applicationData']['userApplicationData'][str(userId)]['queuedQuestions'] = [embed.to_dict()]
                await self.bot.database.save_data(self.bot.botData)
                await ctx.send("This message has been queued (the person you're trying to send to is in the middle of updating their application or responding to a question).")
            else:
                await self._askQuestion(embed, user)
                await ctx.send("Message sent.")

    async def _askQuestion(self, embed, user):
        embedMsg = await user.send(embed=embed)
        await embedMsg.add_reaction('💬')

        modQuestions = self.bot.botData['applicationData']['userApplicationData'][str(user.id)].get('modQuestions')
        if (modQuestions != None):
            self.bot.botData['applicationData']['userApplicationData'][str(user.id)]['modQuestions'].append(embed.to_dict())
        else:
            self.bot.botData['applicationData']['userApplicationData'][str(user.id)]['modQuestions'] = [embed.to_dict()]
        await self.bot.database.save_data(self.bot.botData)

    async def _respond(self, userId, qEmbed):
        guild = self.bot.get_guild(755021484686180432)
        user = get(guild.members, id=userId)

        await user.send('`Your response:`')
        self.bot.botData['applicationData']['userApplicationData'][str(userId)]['activeQuestionSession'] = qEmbed
        await self.bot.database.save_data(self.bot.botData)

    async def _userHasResponded(self, user, message, qEmbed):
        guild = self.bot.get_guild(755021484686180432)
        channel = guild.get_channel(773787257480019979)
        userData = self.bot.botData['applicationData']['userApplicationData'][str(user.id)]
        modMsg = await channel.fetch_message(userData['modMsg'])

        embed = discord.Embed(
            title="Someone responded to a question",
            description=f"The application which this corresponds to is at [this link]({modMsg.jump_url}).",
            color=discord.Color.blue()
        )
        question = discord.Embed.from_dict(userData['modQuestions'][userData['modQuestions'].index(qEmbed)]).description
        embed.add_field(name=f"Q: {question}", value=f"A: {message}")
        await channel.send(embed=embed)
        await user.send("Your response has been sent.")

        userData['modQuestions'].remove(qEmbed)
        userData['activeQuestionSession'] = None

        if (userData.get('queuedQuestions') != None):
            for e in userData['queuedQuestions']:
                embed = discord.Embed.from_dict(e)
                await self._askQuestion(embed, user)
                userData['queuedQuestions'].remove(e)

        self.bot.botData['applicationData']['userApplicationData'][str(user.id)] = userData
        await self.bot.database.save_data(self.bot.botData)

    async def _cancelApplication(self, user):
        self.bot.botData['applicationData']['userApplicationData'][str(user.id)]['sessionActive'] = False
        self.bot.botData['applicationData']['userApplicationData'][str(user.id)]['questionsAsked'] = 0
        await self.bot.database.save_data(self.bot.botData)

    @commands.command()
    async def deleteApplication(self, ctx):
        userData = self.bot.botData['applicationData']['userApplicationData'].get(str(ctx.author.id))
        if ((userData['modMsg'] == None) if userData != None else True):
            await ctx.send("You haven't sent an application.")
            return 

        channel = ctx.guild.get_channel(773787257480019979)
        modMsg = await channel.fetch_message(userData['modMsg'])
        await modMsg.delete()
        self.bot.botData['applicationData']['userApplicationData'].pop(str(ctx.author.id))
        self.bot.botData['applicationData']['modMsgs'].pop(str(modMsg.id))
        await self.bot.database.save_data(self.bot.botData)
        await ctx.send("Your application has been deleted.")

def setup(bot):
    bot.add_cog(ModApplications(bot))