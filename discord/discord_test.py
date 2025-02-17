import discord
import os
from dotenv import load_dotenv

from discord.commands import SlashCommandGroup
from discord.ext import commands, pages


load_dotenv()
# dbot = discord.Bot()
bot = commands.Bot()

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

@bot.slash_command(name="hello", description="Say hello to the bot")
async def hello(ctx: discord.ApplicationContext):
    await ctx.respond("Hey-hou new!")

@bot.slash_command(description="Sends the bot's latency.") # this decorator makes a slash command
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

my_pagetest = SlashCommandGroup("my_pagetest", "Commands for testing ext.pages.")

@my_pagetest.command(name="test")
async def pagetest_default(ctx: discord.ApplicationContext):
    """Demonstrates using the paginator with the default options."""
    paginator = pages.Paginator(pages=test_pages)
    await paginator.respond(ctx.interaction, ephemeral=False)

bot.add_application_command(my_pagetest)

bot.load_extension("cogs.paginator")

# SUREBETS PAGES
@bot.slash_command(name="surebets")
async def command_surebets(ctx: discord.ApplicationContext):
    """Demonstrates using page groups to show surebets."""
    page_groups = [
        pages.PageGroup(
            pages=[
                "Second Set of Pages, Page 1",
            ],
            label="SureBets",
            description="Seznam všech SureBets.",
        ),
        pages.PageGroup(
            pages=[
                "Ukázka sázek",
                "Detail sázkovky",
            ],
            label="Betano",
            description="Detail sázkovky Betano.",
            custom_view=discord.ui.View(discord.ui.Button(style = discord.ButtonStyle.green, label="Test Button, Does Nothing")),
        ),
        pages.PageGroup(
            pages=[
                "Ukázka sázek",
                "Detail sázkovky",
            ],
            label="Fortuna",
            description="Detail sázkovky Fortuna.",
            custom_view=discord.ui.View(discord.ui.Button(style = discord.ButtonStyle.red, label="Test Button, Does Nothing")),
        ),
    ]
    paginator = pages.Paginator(pages=page_groups, show_menu=True)
    await paginator.respond(ctx.interaction, ephemeral=False)


bot.run(os.getenv('MCDUCK_DISCORD_TOKEN'))