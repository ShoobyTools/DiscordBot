import discord
from discord_slash import SlashCommand
from discord.ext import commands
from discord_slash.utils.manage_commands import create_option
import requests
import os
from dotenv import load_dotenv

# shoe stuff
from stockx import stockX
import goat
import stadium_goods
import variants

# crypto stuff
import gas
import dex
import opensea

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
#  NFT
# ==============================================================================

@slash.slash(
    name="gas",
    description="Calculate ETH costs based on gas limit",
    options=[
        create_option(
            name="limit",
            description="The gas limit from the contract",
            option_type=4,
            required=True,
        ),
        create_option(
            name="utilization",
            description="What percentage of the contract the TX will utilize",
            option_type=4,
            required=True,
        ),
        create_option(
            name="price",
            description="The price in ETH for 1 NFT",
            option_type=3,
            required=True,
        ),
        create_option(
            name="number",
            description="The number of mints in one tx",
            option_type=4,
            required=True,
        ),
        create_option(
            name="custom", description="Custom gas price", option_type=4, required=False
        ),
    ],
    guild_ids=GUILD_ID
)
async def _gas(ctx, limit, utilization, price, number, custom=-1):
    costs = gas.calculate(limit, utilization, float(price), number, custom)
    await embed.send_gas(ctx, costs)

@slash.slash(
    name="token-price",
    description="Get a token's price from dextools",
    options=[
        create_option(
            name="token",
            description="Token name or address",
            option_type=3,
            required=True,
        ),
    ],
    guild_ids=GUILD_ID
)
async def _token(ctx, token):
    try:
        await embed.send_token(ctx, dex.check(token))
    except errors.NoTokenFound:
        await ctx.send(f"Token `{token}` not found")
    except errors.Unsupported:
        await ctx.send("Token addresses are not supported at the moment, please use the token symbol instead.")
    except errors.SiteUnreachable:
        await ctx.send("Site unreachable. Try again later.")

@slash.slash(
    name="contract",
    description="Get a token's contract given an Opensea URL",
    options=[
        create_option(
            name="url",
            description="Opensea URL",
            option_type=3,
            required=True,
        ),
    ],
    guild_ids=GUILD_ID
)
async def _contract(ctx, url):
    try:
        await embed.send_contract(ctx, opensea.get_contract(url))
    except errors.Unsupported:
        await ctx.send("Only full Opensea collection URLs are supported at the moment.")
    except errors.SiteUnreachable:
        await ctx.send("Site unreachable. Try again later.")

# ==============================================================================
# StockX
# ==============================================================================

# slash command call
@slash.slash(name="StockX", description="Check StockX prices", guild_ids=GUILD_ID)
async def _stockx(ctx, name: str):
    context = ctx
    try:
        info = stockX(name)
        await embed.send_listing(info, context)
    except errors.NoProductsFound:
        await ctx.send(f"`{name} not found`")
    except errors.SiteUnreachable:
        await ctx.send("`Error accessing StockX site (ERROR 403)`")
    except discord.errors.NotFound:
        await embed.send_listing(info, context)
    except Exception as e:
        await ctx.send("`Unknown error`")
        print("error on " + name)


# .s command call
@client.command(pass_context=True)
async def s(ctx, *args):
    name = ""
    for word in args:
        name += word + " "
    name.strip()
    try:
        info = stockX(name)
        await embed.send_listing(info, ctx)
    except errors.NoProductsFound:
        await ctx.send(f"`{name} not found`")
    except errors.SiteUnreachable:
        await ctx.send("`Error accessing StockX site (ERROR 403)`")
    except Exception as e:
        await ctx.send("`Unknown error`")
        print("error on " + name)


# ==============================================================================
# Goat
# ==============================================================================

# slash command call
@slash.slash(name="Goat", description="Check Goat prices", guild_ids=GUILD_ID)
async def _goat(ctx, name: str):
    try:
        await ctx.send("`Currently not working`")
    except errors.NoProductsFound:
        await ctx.send(f"`{name} not found`")


# .g command call
@client.command(pass_context=True)
async def g(ctx, *args):
    name = ""
    for word in args:
        name += word + " "
    name.strip()
    try:
        await ctx.send("`Currently not working`")
    except errors.NoProductsFound:
        await ctx.send(f"`{name} not found`")


# ==============================================================================
# Stadium Goods
# ==============================================================================

@slash.slash(name="SG", description="Check Stadium Goods prices", guild_ids=GUILD_ID)
async def _sg(ctx, name: str):
    try:
        await ctx.send("`Currently not working`")
    except errors.NoProductsFound:
        await ctx.send(f"`{name} not found`")


# ==============================================================================
# Compare
# ==============================================================================

# @slash.slash(
#     name="Compare",
#     description="Compare prices between StockX and Goat.",
#     guild_ids=GUILD_ID,
# )
# async def _compare(ctx, name):
#     try:
#         await compare.get_prices(name, ctx)
#     except errors.NoProductsFound:
#         await ctx.send("No products found. Try again.")

# # .c command call
# @client.command(pass_context=True)
# async def c(ctx, *args):
#     name = ""
#     for word in args:
#         name += word + " "
#     name.strip()
#     await compare.get_prices(name, ctx)

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
