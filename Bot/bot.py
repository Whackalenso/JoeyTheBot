import discord
from discord.ext import commands
from discord.utils import get
import discordDatabase
import os

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix = '.', case_insensitive = True, intents=intents)
#bot.remove_command('help')

bot.guild = ''
bot.botRole = ''
bot.database = ''
bot.botData = {}

@bot.event
async def on_command_error(ctx, error): #.
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.send('Use all required arguments please.')
	elif isinstance(error, commands.CommandNotFound):
		pass
	else:
		raise error

@bot.event
async def on_ready():
	bot.guild = bot.get_guild(755021484686180432)
	bot.botRole = get(bot.guild.roles, id=755137354888511498)
	bot.database = discordDatabase.Database('Server Soap', 766520404613267476, bot)
	bot.botData = await bot.database.get_data()

	for c in os.listdir('Bot/cogs'):
		bot.load_extension(f"Bot.cogs.{c[:-3]}")

	print("Bot online\nSystems a go-go")
	await bot.change_presence(activity=discord.Game(name="PPC"))
	
@bot.command()
async def roleAmount(ctx, *, roleStr):
	role = get(ctx.guild.roles, name=roleStr)
	if (role != None):
		await ctx.send(f"**{len(role.members)}** people have this role.")
	else:
		await ctx.send("I can't find that role. Don't ping the role, just say what it is. (And it's case sensitive)")

@bot.command()
async def iDontHaveAGroup(ctx):
	role = get(ctx.guild.roles, id=766382143999574037) #Looking For Group role
	if (role not in ctx.author.roles):
		await ctx.author.add_roles(role)
		await ctx.send("You now have the **Looking For Group** role.")
	else:
		await ctx.send("You already have this role.")

@bot.command()
async def iHaveAGroup(ctx):
	mrLeeHistoryRole = get(ctx.guild.roles, id=755232437394604123)
	role = get(ctx.guild.roles, id=766382143999574037) #Looking For Group role
	if (mrLeeHistoryRole in ctx.author.roles):
		if (role in ctx.author.roles):
			await ctx.author.remove_roles(role)
			await ctx.send("The **Looking For Group** role has now been removed from your roles.")
		else:
			await ctx.send("You already don't have this role.")
	else:
		await ctx.send("You don't have Mr. Lee for history so you can't use this command.")

@bot.event
async def on_message(message):
	if ((message.author.id == 690291831564533810) & (message.channel.id == 774365865273065492) &(len(message.attachments) > 0)): #that uesr id is macie and the channel id is cake
		await message.pin()

	await bot.process_commands(message)

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

with open('Bot/token.txt') as t:
	token = t.read()
bot.run(token) #ha L u guys dont have token.txt