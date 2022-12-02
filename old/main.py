import discord
from discord_slash import SlashCommand
from discord.ext import commands
from discord_slash.utils.manage_commands import create_option
import requests
import os
from dotenv import load_dotenv


import embed
import errors

load_dotenv()

TOKEN = os.environ["TOKEN"]
GUILD_ID = [int(os.environ["GUILD_ID"])]
client = commands.Bot(command_prefix=".")
slash = SlashCommand(client, sync_commands=True)


@client.event
async def on_ready():
    print("ready")

    await client.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening, name="Type /info for help"
        )
    )


@slash.slash(
    name="Info",
    description="Provides help on price checker commands",
    guild_ids=GUILD_ID,
)
async def _help(ctx):
    embed = discord.Embed(
        title="Price Checker instructions",
        description="Type `/` before any command to use it.",
        color=0x0008FF,
    )
    embed.add_field(
        name="StockX",
        value="List StockX prices for a shoe or collectible.",
        inline=False,
    )
    embed.add_field(name="Goat", value="List Goat prices for a shoe.", inline=False)
    # embed.add_field(name="Compare", value="Compare StockX and Goat prices.", inline=False)
    embed.add_field(
        name="Vars",
        value="Get Shopify variants and stock if a site has it loaded (i.e. ShoePalace)",
        inline=False,
    )
    embed.add_field(name="⠀", value="⠀", inline=False)
    embed.add_field(
        name="Alternate Price Checker instructions",
        value="Type `.` before any command to use it.",
        inline=False,
    )
    embed.add_field(
        name="s",
        value="List StockX prices for a shoe or collectible.",
        inline=False,
    )
    embed.add_field(name="g", value="List Goat prices for a shoe.", inline=False)
    # embed.add_field(name="c", value="Compare StockX and Goat prices.", inline=False)
    await ctx.send(embed=embed)


# ==============================================================================
# Variants
# ==============================================================================


@slash.slash(
    name="Vars",
    description="Get Shopify variants",
    guild_ids=GUILD_ID,
    options=[
        create_option(
            name="link",
            description="Link to get vars from",
            option_type=3,
            required=True,
        ),
        create_option(
            name="nohalf",
            description="Remove half sizing in variants list",
            option_type=5,
            required=False,
        ),
    ],
)
async def _variants(ctx, link, nohalf=False):
    await variants.get_vars(link, nohalf, ctx)


client.run(TOKEN)
