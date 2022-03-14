import asyncio
import string
import random
import json
import os
import discord

from discord.ext import commands

BOT_TOKEN = ""

class scrabble:
    def __init__(self):
        self.letters_points = {"aeioulnstr": 1, "dg": 2, "bcmp": 3, "fhvwy": 4, "k": 5, "jx": 8, "qz": 10}
        self.letters = ""
        self.setup()    

    def setup(self):
        with open(f"{os.path.dirname(os.path.realpath(__file__))}\\words.json") as file:
            self.words = json.loads(file.read())

        letter = random.choice(string.ascii_lowercase)

        while len(self.letters) <= 10:
            if letter not in self.letters:
                self.letters += letter
            letter = random.choice(string.ascii_lowercase)  

    def validate_word(self, word):
        if word in self.words and len(word) <= 15:
            return True
        return False
    
    def calculate_score(self, word):
        if self.validate_word(word):
            letters = ""
            score = 0

            for i in word:
                if i in self.letters and i not in letters:
                    for j in self.letters_points:
                        if i in j:
                            score += self.letters_points[j]
                else:
                    score = 0
                    break

            return score
        return 0

running_games = {}
waiting_games = []

participants = {}

client = commands.Bot(command_prefix = '.')

async def handle_start(chan_id):
    await asyncio.sleep(10)
        
    waiting_games.remove(chan_id)
    running_games[chan_id] = scrabble()

async def handle_finish(chan_id):
    await asyncio.sleep(30)

    h = max(participants[chan_id].items(), key=lambda k: k[1])
    highest, highest_score = h[0], h[1] 
    
    if highest_score > 0:
        await client.get_channel(chan_id).send(embed=discord.Embed().add_field(name="Game ended!",value=f"The winner was <@{highest}> with a score of {highest_score}."))
    else:
        await client.get_channel(chan_id).send(embed=discord.Embed().add_field(name="Game ended!",value=f"No one has won this game."))
    
    del running_games[chan_id]

@client.event
async def on_ready():
    print("Bot started")

@client.command()
async def start(ctx):
    if ctx.channel.id not in running_games and ctx.channel.id not in waiting_games:
        waiting_games.append(ctx.channel.id)
        participants[ctx.channel.id] = {}

        await client.get_channel(ctx.channel.id).send(embed=discord.Embed().add_field(
            name="Game starting",
            value="Type JOIN to participate, starting in 10 seconds"
        ))

        await handle_start(ctx.channel.id)
        await ctx.channel.send(embed=discord.Embed().add_field(name="Game started!",value=f"You have **30 seconds**. Send valid english words that contain only the given letters: **{running_games[ctx.channel.id].letters}**"))
        if len(participants[ctx.channel.id]) > 0:
            await handle_finish(ctx.channel.id)
        else:
            await ctx.channel.send("No one participated, so the game was cancelled.")

    else:
        await client.get_channel(ctx.channel.id).send(embed=discord.Embed(title="Fail").add_field(
            name="Unable to start the game",
            value="A game is already started."
        ))

@client.event
async def on_message(ctx):
    if ctx.channel.id in waiting_games:        
        if ctx.author.id not in participants[ctx.channel.id] and ctx.content == "JOIN":
            participants[ctx.channel.id][ctx.author.id] = 0
    elif ctx.channel.id in running_games and ctx.author.id in participants[ctx.channel.id]:
        game = running_games[ctx.channel.id]

        participants[ctx.channel.id][ctx.author.id] = game.calculate_score(ctx.content)
    await client.process_commands(ctx)

client.run(BOT_TOKEN)
