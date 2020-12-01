import discord
from discord.ext import commands
from better_profanity import profanity #i just realized that since im hosting this, its different from when i dont. i changed the code to the package locally.
import re

class ContentFilter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open(f'{bot.mainFolder}/Bot/profanity_wordlist.txt', 'r') as f: 
            self.word_list = f.read().splitlines()
        for word in range(len(self.word_list)):
            self.word_list[word] = list(profanity._generate_patterns_from_word(self.word_list[word]))
        self.enabled = True
        self.wordsThatNeedToBeByThemselves = ['ass', 'cum', 'tit', 'semen', 'anal', 'cock']
        self.servers = [755021484686180432]

    async def cog_check(self, ctx):
        return ctx.guild.id in self.servers

    async def onOff(self, _ctx, _bool, _string):
        if (_ctx.message.author.guild_permissions.administrator):
            if (self.enabled == _bool):
                await _ctx.send(f"I'm already {_string}d.")
            else:
                self.enabled = _bool
        else:
            await _ctx.send("You need admin perms to do this.")

    @commands.command()
    async def enable(self, ctx):
        await self.onOff(ctx, True, "enable")

    @commands.command()
    async def disable(self, ctx):
        await self.onOff(ctx, False, "disable")

    @commands.Cog.listener()
    async def on_message(self, message):
        if not await self.cog_check(message):
            return
            
        punished = False

        async def punish(word):
            await message.delete()
            await message.channel.send(f"{message.author.name}'s message contained inappropriate content so it was deleted.")
            print(f"{message.content} | {word} | {message.author}")
            punished = True

        def filterContent(content, word):
            wordIndex = 0
            newContent = []
            #if (word[0] in content): #huge timesave bruh im able to skip like all the words except the one that i need o wait i think i can put this in a better spot
            for i in range(len(content)):
                if (content[i] == word[wordIndex]):
                    wordIndex += 1
                    newContent.append(word[wordIndex - 1])
                    if (wordIndex == len(word)):
                        return ''.join(newContent)
                elif (content[i] != word[wordIndex - 1]):
                    wordIndex = 0
                    newContent = []
            return ''

        def isWordByItself(content, word):
            words = content.split(' ')
            for _word in words:
                if (word == _word):
                    return True

            return False

        def removeSpoilers(string):
            split = string.split('||')
            newSplit = []
            for i in range(len(split)):
                if ((i % 2 == 0) or (split[i] == split[-1])):
                    newSplit.append(split[i])
            newString = ''.join(newSplit)
            return newString

        async def bigBoiFunction(newcontent):
            for wordcombos in self.word_list:
                for word in wordcombos:
                    word = str(word)
                    if ((word in newcontent) & (word.isnumeric() == False) & (word != '7/7')):

                        if (word not in self.wordsThatNeedToBeByThemselves):
                            await punish(word)
                            return True
                        else:
                            if (isWordByItself(newcontent, word)):
                                await punish(word)
                                return True

            for wordcombos in self.word_list:
                for word in wordcombos:
                    word = str(word)
                    wordIsntByItself = all([word != w for w in self.wordsThatNeedToBeByThemselves])
                    if ((word[0] in newcontent) & (wordIsntByItself) & (word.isnumeric() == False) & (word != '7/7')):
                        if (word == filterContent(newcontent, word)):
                            await punish(word)
                            return True

            return False

        def makeNewContent(removeSpoilersBool):
            emojis = re.findall(r'<:\w*:\d*>', message.content)
            lower = message.content.lower()
            for e in emojis:
                lower = lower.replace(e, '')
            stringThing = lower
            if (removeSpoilersBool):
                newcontent = removeSpoilers(lower)
                stringThing = newcontent
            newcontent = stringThing.translate(lower.maketrans('', '', '''"#%&'(),-.:;<=>?[\]^_{|}~`*''')) #not |
            return newcontent

        if ((self.enabled) & (not message.author.bot)):
            newcontent = makeNewContent(False)

            funct = await bigBoiFunction(newcontent)
            if (funct == False):
                newcontent = makeNewContent(True)
                await bigBoiFunction(newcontent)

        if ((message.author.id == 235088799074484224) & (message.channel.id == 760301930437148722)):
            await message.delete()

def setup(bot):
    bot.add_cog(ContentFilter(bot))