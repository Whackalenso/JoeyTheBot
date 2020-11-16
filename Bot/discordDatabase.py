import discord
from discord.utils import get
import json
import io

class Database:
	def __init__(self, name, serverId, bot, **extra):
		self.bot = bot
		self.name = name
		self.server = bot.get_guild(serverId)
		self.database_category = get(self.server.categories, name=name)

		self.default_collection = extra.get('default_collection_name') if extra.get('default_collection_name') != None else 'general'
		
		if (self.server == None):
			raise BotNotFound('This bot is not connected to the database server')

	async def create(self, **extra):
		if (self.name in (c.name for c in self.server.categories)):
			raise NameAlreadyExists('This database name already exists')

		self.database_category = await self.server.create_category(self.name)
		await self.database_category.create_text_channel(self.default_collection)

	async def delete(self):
		if (self.database_category == None):
			raise DatabaseNotFound("This database doesn't exist in the database server")

		for c in self.database_category.channels:
			await c.delete()
		await self.database_category.delete()

	async def create_collection(self, name):
		if (self.database_category == None):
			raise DatabaseNotFound("This database doesn't exist in the database server")

		return await self.database_category.create_text_channel(name)

	async def delete_collection(self, collection:discord.TextChannel):
		await collection.delete()

	async def save_data(self, data, **extra):
		collection = extra.get('collection') if extra.get('collection') != None else self.default_collection
		for c in self.database_category.channels:
			if (c.name == collection):
				collection = c
				break
		history = await collection.history(limit=None).flatten() #might be slow?

		path = f'tempData/tempData_{len(history)}.json'
		with open(path, 'w') as f:
			json.dump(data, f, indent=4)

		await collection.send(file=discord.File(path))

	async def get_data(self, **extra):
		collection = extra.get('collection') if extra.get('collection') != None else self.default_collection
		for c in self.database_category.channels:
			if (c.name == collection):
				collection = c
				break
		messages = await collection.history().flatten()
		data = messages[extra.get('position')] if extra.get('position') != None else messages[0]

		tempFile = io.BytesIO()
		await data.attachments[0].save(tempFile)
		data = io.BytesIO(tempFile.getvalue())

		return json.loads(data.read())

class BotNotFound(Exception):
	pass
class NameAlreadyExists(Exception):
	pass
class DatabaseNotFound(Exception):
	pass