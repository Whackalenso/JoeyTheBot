import discord
from discord.ext import commands, tasks
from discord.utils import get
import discordDatabase
import os
import heroku3
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import requests
import asyncio
import io

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='.', case_insensitive=True, intents=intents)
#bot.remove_command('help')

bot.guild = ''
bot.botRole = ''
bot.database = ''
bot.botData = {}
bot.mainFolder = 'JoeyTheBot'
# for d in next(os.walk('.'))[1]:
# 	if (not d.startswith('.')):
# 		bot.mainFolder = d
# 		break

def updateData(database, data, **extra):
	exclude = extra.get('exclude')
	for name in bot.cogs:
		if (exclude != name):
			cog = bot.get_cog(name) # we do this instead of just using c because according to the docs, its just readonly
			cog.bot.botData = data
			cog.bot.database = database

@bot.event
async def on_command_error(ctx, error): #.
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.send('Use all required arguments please.')
	elif isinstance(error, commands.CommandNotFound) or isinstance(error, commands.errors.CheckFailure):
		pass
	else:
		raise error

@bot.event
async def on_ready():
	bot.database = discordDatabase.Database('Server Soap', 766520404613267476, bot)
	bot.botData = await bot.database.get_data()

	bot.guild = bot.get_guild(755021484686180432)
	bot.botRole = get(bot.guild.roles, id=755137354888511498)

	for c in os.listdir(f'{bot.mainFolder}/Bot/cogs'):
		if (c != '__pycache__'):
			cogStr = f"{bot.mainFolder}.Bot.cogs.{c[:-3]}"
			bot.load_extension(cogStr)
			print(f"Loaded cog: {cogStr}")

	#newsLoop.start()

	print("Bot online\nSystems a go-go")
	await bot.change_presence(activity=discord.Activity(name="btw if im not responding it might just be cuz im slow",type=discord.ActivityType.playing))

@bot.command()
async def members(ctx):
	membs = ctx.guild.members
	stufs = {
		"Not Verified": [0, ctx.guild.get_role(755146208623984741)],
		"Bots": [0, ctx.guild.get_role(755137354888511498)],
		"7th Grade": [0, ctx.guild.get_role(755166578290458654)],
		"8th Grade": [0, ctx.guild.get_role(755166669856440512)],
		"Not Korematsu Student": [0, ctx.guild.get_role(773395171420667923)]}
	items = list(stufs.items())
	for m in membs:
		for n, v in items:
			if v[1] in m.roles:
				stufs[n][0] += 1
	
	embed = discord.Embed( 
		description=f"*Total Members - **{len(membs)}***", 
		color=discord.Color.blue())
	embed.set_author(name="Server Members", icon_url=ctx.guild.icon_url)
	for i in [list(items[0]), list(items[1])]:
		embed.add_field(name=i[0], value=i[1][0], inline=False)

	# Pie chart, where the slices will be ordered and plotted counter-clockwise:
	gradeList = [list(items[2]), list(items[3]), list(items[4])]

	fig1, ax1 = plt.subplots()
	values = [g[1][0] for g in gradeList]
	def my_autopct(pct):
		total = sum(values)
		val = int(round(pct*total/100.0))
		return '{p:.0f}%  ({v:d})'.format(p=pct,v=val)

	ax1.pie(values, labels=[g[0] for g in gradeList], autopct=my_autopct, startangle=90)
	ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
	plt.savefig('tempFig.png', bbox_inches = 'tight',)
	embed.set_image(url="attachment://tempFig.png")
	_file = discord.File('tempFig.png')
	
	await ctx.send(embed=embed, file=_file)

@bot.command()
async def reviveCyberweb(ctx):
	heroku = heroku3.from_key(bot.herokuKey)
	app = heroku.apps()[0]

	if app.dynos()[0].state == 'down':
		await ctx.send("Cyberweb seems to be down for a reason. Ask Nigel about this if you want.")
	else:
		app.restart()
		await ctx.send("Cyberweb has been restarted and will be online shortly.") # `(If this doesn't work, it may be that Cyberweb ran out of free hosting for the month and will come back next month)`
	
@bot.command()
async def roleAmount(ctx, *, roleStr):
	role = get(ctx.guild.roles, name=roleStr)
	if (role != None):
		await ctx.send(f"**{len(role.members)}** people have this role.")
	else:
		await ctx.send("I can't find that role. Don't ping the role, just say what it is. (And it's case sensitive)")

@bot.event
async def on_message(message):
	if message.guild.id == 755021484686180432:
		if ((message.author.id == 690291831564533810) & (message.channel.id == 774365865273065492) &(len(message.attachments) > 0)): #that uesr id is macie and the channel id is cake
			await message.pin()

	await bot.process_commands(message)

@tasks.loop(minutes=1)
async def checkIfCyberdead():
	if bot.cyberweb.status == discord.Status.offline:
		await reviveCyberweb(bot.redditChan)

@checkIfCyberdead.before_loop
async def cyberdead_before_loop():
	await bot.wait_until_ready()
	korem = bot.get_guild(755021484686180432)
	bot.cyberweb = korem.get_member(738628391908933683)
	bot.redditChan = korem.get_channel(773383060653604874)

@bot.event
async def on_guild_emojis_update(guild, before, after):
	channel = guild.get_channel(755021484686180435) #announcements
	if channel == None: #just in case
		return

	updates = [] #it should only be one but it returns a list so imma just do a list just in case somehow there can be multiple updates in 1 event
	updateType = ''
	removed = False
	if len(after) < len(before):
		updates = [e for e in before if e not in after]
		updateType = "removed from the server :("
		removed = True
	else:
		updates = [e for e in after if e not in before]
		if len(before) == len(after):
			updateType = "updated" #I'm pretty sure this won't actually happen but just in case u kno
		else:
			updateType = "added to the server :)"

	for u in updates:
		img = None
		if removed:
			f = io.BytesIO()
			await u.url_as().save(f)
			img = discord.File(f, filename=str(u)+'.png')
		await channel.send(content=f"The emoji {u} was {updateType}", file=img)

# @bot.event
# async def on_member_update(before, after):
# 	_role = await get()
# 	if (_role in after.roles) & (before.roles != after.roles):
# 		isUserReady = await self._isUserReady(after)
# 		if (isUserReady):
# 			await self._userIsReady(after)

# @bot.command()
# async def help(ctx): # , *, _arg:Union[str, None]
# 	verificationValue = '''`.setName <your name>` | Sets your name.
# `.setSchedule <your schedule>` | Sets your schedule. Your schedule should be all your periods starting from homeroom and separated by commas. If you have an extra class you can include it as well at the end. `Example: Mr. U, Mr. Lee - History, Ms. Carrico - Band, Mr. Pohl - Science, Mr. Lee - Geometry, Mr. Carrol - Pe, Ms. Davis - English, Ms. Carrico - Jazz Ensenble`'''
# 	adminValue = '''`.moveMessage`'''
# 	otherValue = ''''''

# 	embed = discord.Embed(
# 		title="Joey the bot help",
# 		color=discord.Color.gold()
# 	)
# 	embed.add_field(name="Verification", value=verificationValue)
# 	if (ctx.author.guild_permissions.administrator): embed.add_field(name="Admin", value=adminValue)
# 	embed.add_field(name="Other", value=otherValue)
# 	embed.set_footer(text="All commands all case insensitive (whether you use capital letters doesn't matter for typing a command). Also don't actually include the <>.")

if (__name__ == '__main__'):
	#prob dont need to do ./ but eh
	with open('./herokuKey.txt') as f:
		bot.herokuKey = f.read()

	with open('./token.txt') as t:
		token = t.read()
	
	#checkIfCyberdead.start()
	bot.run(token)
