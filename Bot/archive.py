# pylint: skip-file

@bot.command(aliases=['moveMessages'])
async def moveMessage(ctx, id:Union[int, str], newChannel:discord.TextChannel):
	if (ctx.author.guild_permissions.administrator):
		if (ctx.channel.id != newChannel.id):
			async with ctx.typing():

				msg = None
				msgs = None
				if (isinstance(id, int)):
					msg = await ctx.channel.fetch_message(id)
					if (msg == None):
						await ctx.send("Either this id is wrong, or the message doesn't exist in this channel. (Use this command in the channel the message exists in)")
						return
				elif (isinstance(id, str)):
					idList = id.lower().split('-')
					history = await ctx.channel.history(limit=5).flatten()
					if ((len(history) > 1) == False):
						await ctx.send("There's no messages in this channel yet.")
						return

					if (id.lower() == 'recent'):
						msg = history[1]
					elif (len(idList) == 2):
						if (all(i.isnumeric() for i in idList)):
							msgs = await getMessagesFromRange(ctx.channel.history(), int(idList[0]), int(idList[1]))
						elif ((idList[0] == 'recent') & (idList[1].isnumeric())):
							msgs = await getMessagesFromRange(ctx.channel.history(), history[1].id, int(idList[1]))
						else:
							await ctx.send(f"I don't know what you mean by **{id}**.")
					else:
						await ctx.send(f"I don't know what you mean by **{id}**.")

				if (msg != None):
					await moveMessageHelper(ctx, newChannel, msg)
				elif (msgs != None):
					await moveMessagesHelper(ctx, newChannel, msgs)
				else:
					print("An error has occured. Both msg and msgs are None.")

		else:
			await ctx.send("That's the same channel that you're currently in. Make sure to do a different one.")
	else:
		await ctx.send("You need admin perms to do this.")

@bot.command()
async def acceptTerms(ctx):
	if (bot.notVerifiedRole in ctx.author.roles):
		if (ctx.author.id not in bot.usersAccepted):
			await _userAccept(ctx.author)
			if (bot.acceptMsgs[ctx.author.id] != None):
				await bot.acceptMsgs[ctx.author.id].delete()
		else:
			await ctx.send("You've already accepted the terms.")
	else:
		await ctx.send("You're already verified.")

async def _userAccept(user:discord.Member):
	if (user.id not in bot.usersAccepted):
		bot.usersAccepted.append(user.id)
	#await bot.channel.send("You have accepted the terms.")

#How to download an attachment then store it as a discord.File:

path = f"files/{att.filename}"
_file = open(path,'wb')
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'}
req = urllib.request.Request(att.url, headers=headers)
_file.write(urllib.request.urlopen(req).read())
_file.close()
files.append(discord.File(path))

#How to download an avatar and take the first frame of it (so if its animated) (uses Pillow)

async with aiohttp.ClientSession() as session: # I think there's an easier way to do this with discord. Look at discord.Asset
	async with session.get(str(msg.author.avatar_url)) as resp:
		if resp.status != 200:
			return print('Could not download file...')

		data = io.BytesIO(await resp.read())
		with Image.open(data) as im:
			im.seek(0)
			_obj = io.BytesIO()
			im.save(_obj, 'PNG')
			data = io.BytesIO(_obj.getvalue())

#in on_raw_reaction_add:

if (user.id not in bot.usersAccepted):
	reactionForVerification = False
	userForVerificationMsg = '' #discord.Member.id
	for member, msg in bot.acceptMsgs.items():
		if (reaction.message.id == bot.acceptMsgs[member].id):
			userForVerificationMsg = member
			reactionForVerification = True

	if (reactionForVerification == True):
		if (reaction.emoji != "👍"):
			await reaction.clear()
		elif (userForVerificationMsg != user.id):
			await reaction.remove(user)
		else:
			await _userAccept(user)
			await bot.acceptMsgs[user.id].delete()
			if (_isUserReady(user)):
				await _userIsReady(user)

@bot.command()
async def setSchedule(ctx, *, args):
	if (ctx.message.channel == bot.channel):
		if (args.lower() == "not student"):
			bot.botData['schedules'][str(ctx.author.id)] = "not student"
			await ctx.send("Your schedule has been skipped")
			isUserReady = await _isUserReady(ctx.author)
			if (isUserReady):
				await _userIsReady(ctx.author)

			await bot.database.save_data(bot.botData)
			return

		if (args[-1] == ','):
			await ctx.send("You have a comma at the end :|")
			return

		periods = args.split(',')

		if (len(periods) < 7):
			await ctx.send(f"I think you're missing something, because you only have {len(periods)} periods listed in here. There should be at least 7 periods including homeroom and not including lunch.")
		else:
			bot.botData['schedules'][str(ctx.author.id)] = periods #bot.schedules, ctx.author.id
			history = await bot.schedulesChannel.history().flatten()
			for message in history:
				if (len(message.embeds) > 0):
					if (ctx.author.nick != None):
						if (ctx.author.nick in message.embeds[0].title):
							await message.delete()

			await ctx.send("Your schedule has been set")

			if (bot.notVerifiedRole in ctx.author.roles):
				isUserReady = await _isUserReady(ctx.author)
				if (isUserReady):
					await _userIsReady(ctx.author)
			else:
				await putScheduleInChannel(ctx.author, periods)

			await bot.database.save_data(bot.botData)
	else:
		msg = await ctx.send(f"Do this in {bot.channel.mention} please.")
		time.sleep(5)
		await ctx.message.delete()
		await msg.delete()