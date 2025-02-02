import discord
import os
from dotenv import load_dotenv

load_dotenv()
bot = discord.Bot()

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

# @bot.slash_command(name="hello", description="Say hello to the bot")
# async def hello(ctx: discord.ApplicationContext):
#     await ctx.respond("Hey!")

@bot.command(description="Sends the bot's latency.") # this decorator makes a slash command
async def ping(ctx): # a slash command will be created with the name "ping"
    await ctx.respond(f"Pong! Latency is {bot.latency}")

bot.run(os.getenv('MCDUCK_DISCORD_TOKEN'))