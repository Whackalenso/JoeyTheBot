import discord
from discord.ext import commands, tasks
from discord.utils import get
import discordDatabase
import os
import heroku3

intents = discord.Intents.all() #defalt()
# intents.members = True
# intents.presences = True
bot = commands.Bot(command_prefix='.', case_insensitive=True, intents=intents)
#bot.remove_command('help')

bot.guild = ''
bot.botRole = ''
bot.database = ''
bot.botData = {}
for d in next(os.walk('.'))[1]:
	if (not d.startswith('.')):
		bot.mainFolder = d
		break

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

	print("Bot online\nSystems a go-go")
	await bot.change_presence(activity=discord.Activity(name="PPC",type=discord.ActivityType.watching))

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

#NewsChannel --------------------------------------------------------------------------------*

#Command to set the News Channel
@bot.command()
async def setNewsChannel(ctx, channel:discord.TextChannel):
    _newsChannel = channel.id
    await ctx.send(f"News Channel set to {channel.mention}")
@bot.command()
async def newsUpdateTimeOut(ctx, hours):
    _updateTime = hours/60
    _outString = f"Set News Update Timeout to {hours} hours" if hours > 24 else f"Set News Update Timeout to {hours} hours. IT IS RECOMMENDED TO KEEP THE VALUE LARGER THAN 24 TO AVOID REPOSTING.
    await ctx.send(_outString)

#Function to get certain headlines
def get_element_text(list_of_elements, n):
	number_of_elements = n
	elements = list_of_elements
	element_text = []
	for i in range(number_of_elements):
		element_text.append(elements[i].get_text())

	return element_text
#Main loops that executes once per day(or specified update time)
@tasks.loop(minutes=_updateTime)
async def newsLoop():
	#Scrape BBC and extract the headlines
	URL = requests.get("https://www.bbc.co.uk/news")
	soup = BeautifulSoup(URL.text, 'html.parser')
	headlines = soup.select(".gs-c-promo-heading__title")
	Heads = get_element_text(headlines,10)
	for x in Heads:
		await _newsChannel.send(Heads[x])
	


			
	

---------------------------------------------------------------------------------------------*
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
async def before_loop():
	await bot.wait_until_ready()
	korem = bot.get_guild(755021484686180432)
	bot.cyberweb = korem.get_member(738628391908933683)
	bot.redditChan = korem.get_channel(773383060653604874)

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
	newsLoop.start()
	bot.run(token)
