import discord
from discord_slash import SlashCommand
from discord.ext import commands
from discord_slash.context import ComponentContext
from discord_slash.utils.manage_components import wait_for_component

import os
from dotenv import load_dotenv

import stockx
import goat
import stadium_goods
import compare
import variants

import embed
import errors

load_dotenv()

TOKEN = os.environ["TOKEN"]
GUILD_ID = [int(os.environ["GUILD_ID"])]
client = commands.Bot(command_prefix=".")
slash = SlashCommand(client, sync_commands=True)


@client.event
async def on_ready():
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
    await ctx.send(embed=embed)

# ==============================================================================
# StockX
# ==============================================================================

@slash.slash(name="StockX", description="Check StockX prices", guild_ids=GUILD_ID)
async def _stockx(ctx, name: str):
    try:
        info = stockx.get_prices(name)
        await embed.send_listing(info, ctx)
        while True:
            button_ctx: ComponentContext = await wait_for_component(client, components=embed.stockx_button_row)
            if button_ctx.component["custom_id"] == "stockx_profit_button1":
                await embed.send_profit(info, button_ctx, 1)
            elif button_ctx.component["custom_id"] == "stockx_profit_button2":
                await embed.send_profit(info, button_ctx, 2)
            elif button_ctx.component["custom_id"] == "stockx_profit_button3":
                await embed.send_profit(info, button_ctx, 3)
            elif button_ctx.component["custom_id"] == "stockx_profit_button4":
                await embed.send_profit(info, button_ctx, 4)
    except errors.NoProductsFound:
        await ctx.send("No products found. Try again.")
    except errors.SiteUnreachable:
        await ctx.send("Error accessing StockX site (ERROR 403)")

@client.command(pass_context=True)
async def s(ctx, *args):
    name = ""
    for word in args:
        name += word + " "
    name.strip()
    try:
        info = stockx.get_prices(name)
        await embed.send_listing(info, ctx)
    except errors.NoProductsFound:
        await ctx.send("No products found. Try again.")
    except errors.SiteUnreachable:
        await ctx.send("Error accessing StockX site (ERROR 403)")

# ==============================================================================
# Goat
# ==============================================================================

@slash.slash(name="Goat", description="Check Goat prices", guild_ids=GUILD_ID)
async def _goat(ctx, name: str):
    try:
        info = goat.get_prices(name)
        await embed.send_listing(info, ctx)
        while True:
            button_ctx: ComponentContext = await wait_for_component(client, components=embed.goat_button_row)
            if button_ctx.component["custom_id"] == "goat_profit_button":
                await embed.send_profit(info, button_ctx, 0)
    except errors.NoProductsFound:
        await ctx.send("No products found. Try again.")

@client.command(pass_context=True)
async def g(ctx, *args):
    name = ""
    for word in args:
        name += word + " "
    name.strip()
    try:
        info = goat.get_prices(name)
        await embed.send_listing(info, ctx)
    except errors.NoProductsFound:
        await ctx.send("No products found. Try again.")

# ==============================================================================
# Stadium Goods
# ==============================================================================


@slash.slash(name="SG", description="Check Stadium Goods prices", guild_ids=GUILD_ID)
async def _sg(ctx, name: str):
    try:
        info = stadium_goods.get_prices(name)
        await embed.send_listing(info, ctx)
        while True:
            button_ctx: ComponentContext = await wait_for_component(client, components=embed.sg_button_row)
            if button_ctx.component["custom_id"] == "sg_profit_button":
                await embed.send_profit(info, button_ctx, 0)
    except errors.NoProductsFound:
        await ctx.send("No products found. Try again.")

# ==============================================================================
# Compare
# ==============================================================================

@slash.slash(
    name="Compare",
    description="Compare prices between all 3 sites.",
    guild_ids=GUILD_ID,
)
async def _compare(ctx, name):
    try:
        await compare.get_prices(name, ctx)
    except errors.NoProductsFound:
        await ctx.send("No products found. Try again.")

# ==============================================================================
# Variants
# ==============================================================================

@slash.slash(name="Vars", description="Get Shopify variants", guild_ids=GUILD_ID)
async def _variants(ctx, link):
    await variants.get_vars(link, ctx)


client.run(TOKEN)
