import discord
import os
from dotenv import load_dotenv

from discord.commands import SlashCommandGroup
from discord.ext import commands, pages


load_dotenv()
bot = discord.Bot()

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

@bot.slash_command(name="hello", description="Say hello to the bot")
async def hello(ctx: discord.ApplicationContext):
    await ctx.respond("Hey-hou new!")

@bot.command(description="Sends the bot's latency.") # this decorator makes a slash command
async def ping(ctx): # a slash command will be created with the name "ping"
    await ctx.respond(f"Pong! Latency is {bot.latency}, bro <3")


test_pages = [
    "Page 1",
    [
        discord.Embed(title="Page 2, Embed 1"),
        discord.Embed(title="Page 2, Embed 2"),
    ],
    "Page Three",
    discord.Embed(title="Page Four"),
    discord.Embed(
        title="Page Five",
        fields=[
            discord.EmbedField(
                name="Example Field", value="Example Value", inline=False
            ),
        ],
    ),
    [
        discord.Embed(title="Page Six, Embed 1"),
        discord.Embed(title="Page Seven, Embed 2"),
    ],
]

pagetest = SlashCommandGroup("pagetest", "Commands for testing ext.pages.")

@pagetest.command(name="test")
async def pagetest_default(ctx: discord.ApplicationContext):
    """Demonstrates using the paginator with the default options."""
    paginator = pages.Paginator(pages=test_pages)
    await paginator.respond(ctx.interaction, ephemeral=False)

bot.add_application_command(pagetest)


bot.run(os.getenv('MCDUCK_DISCORD_TOKEN'))