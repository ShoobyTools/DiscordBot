import discord
from discord_slash import SlashCommand
from discord.ext import commands
from discord_slash.context import ComponentContext
from discord_slash.utils.manage_components import wait_for_component

import time
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

# on button press
# level 1
@slash.component_callback()
async def stockx_profit_button1(ctx: ComponentContext):
    title = ctx.origin_message.embeds[0].title
    info = stockx.get_prices(title)
    try:
        await embed.send_profit(info, ctx, 1)
    except errors.NoRetailPrice:
        await ctx.edit_origin(content="Retail price not available.")
    except discord.errors.NotFound:
        await embed.send_profit(info, ctx, 1)

# level 2
@slash.component_callback()
async def stockx_profit_button2(ctx: ComponentContext):
    title = ctx.origin_message.embeds[0].title
    info = stockx.get_prices(title)
    try:
        await embed.send_profit(info, ctx, 2)
    except errors.NoRetailPrice:
        await ctx.edit_origin(content="Retail price not available.")
    except discord.errors.NotFound:
        await embed.send_profit(info, ctx, 2)

# level 3
@slash.component_callback()
async def stockx_profit_button3(ctx: ComponentContext):
    title = ctx.origin_message.embeds[0].title
    info = stockx.get_prices(title)
    try:
        await embed.send_profit(info, ctx, 3)
    except errors.NoRetailPrice:
        await ctx.edit_origin(content="Retail price not available.")
    except discord.errors.NotFound:
        await embed.send_profit(info, ctx, 3)

# level 4
@slash.component_callback()
async def stockx_profit_button4(ctx: ComponentContext):
    title = ctx.origin_message.embeds[0].title
    info = stockx.get_prices(title)
    try:
        await embed.send_profit(info, ctx, 4)
    except errors.NoRetailPrice:
        await ctx.edit_origin(content="Retail price not available.")
    except discord.errors.NotFound:
        await embed.send_profit(info, ctx, 4)

@slash.component_callback()
async def stockx_listing_button(ctx: ComponentContext):
    title = ctx.origin_message.embeds[0].title
    info = stockx.get_prices(title)
    try:
        await embed.send_listing(info, ctx, True)
    except discord.errors.NotFound:
        await embed.send_listing(info, ctx, True)

# slash command call
@slash.slash(name="StockX", description="Check StockX prices", guild_ids=GUILD_ID)
async def _stockx(ctx, name: str):
    context = ctx
    try:
        info = stockx.get_prices(name)
        await embed.send_listing(info, context, False)
    except errors.NoProductsFound:
        await ctx.send("No products found. Try again.")
    except errors.SiteUnreachable:
        await ctx.send("Error accessing StockX site (ERROR 403)")
    except discord.errors.NotFound:
        await embed.send_listing(info, context, False)

# .s command call
@client.command(pass_context=True)
async def s(ctx, *args):
    name = ""
    for word in args:
        name += word + " "
    name.strip()
    try:
        info = stockx.get_prices(name)
        await embed.send_listing(info, ctx, False)
    except errors.NoProductsFound:
        await ctx.send("No products found. Try again.")
    except errors.SiteUnreachable:
        await ctx.send("Error accessing StockX site (ERROR 403)")

# ==============================================================================
# Goat
# ==============================================================================

# on button press
@slash.component_callback()
async def goat_profit_button(ctx: ComponentContext):
    title = ctx.origin_message.embeds[0].title
    info = goat.get_prices(title)
    try:
        await embed.send_profit(info, ctx, 0)
    except errors.NoRetailPrice:
        await ctx.edit_origin(content="Retail price not available.")

@slash.component_callback()
async def goat_listing_button(ctx: ComponentContext):
    title = ctx.origin_message.embeds[0].title
    info = goat.get_prices(title)
    await embed.send_listing(info, ctx, True)

# slash command call
@slash.slash(name="Goat", description="Check Goat prices", guild_ids=GUILD_ID)
async def _goat(ctx, name: str):
    try:
        info = goat.get_prices(name)
        await embed.send_listing(info, ctx, False)
    except errors.NoProductsFound:
        await ctx.send("No products found. Try again.")

# .g command call
@client.command(pass_context=True)
async def g(ctx, *args):
    name = ""
    for word in args:
        name += word + " "
    name.strip()
    try:
        info = goat.get_prices(name)
        await embed.send_listing(info, ctx, False)
    except errors.NoProductsFound:
        await ctx.send("No products found. Try again.")

# ==============================================================================
# Stadium Goods
# ==============================================================================

# on button press
@slash.component_callback()
async def sg_profit_button(ctx: ComponentContext):
    title = ctx.origin_message.embeds[0].title
    info = stadium_goods.get_prices(title)
    try:
        await embed.send_profit(info, ctx, 0)
    except errors.NoRetailPrice:
        await ctx.edit_origin(content=":red_square: Retail price not available. :red_square:")

@slash.component_callback()
async def sg_listing_button(ctx: ComponentContext):
    title = ctx.origin_message.embeds[0].title
    info = stadium_goods.get_prices(title)
    await embed.send_listing(info, ctx, True)

@slash.slash(name="SG", description="Check Stadium Goods prices", guild_ids=GUILD_ID)
async def _sg(ctx, name: str):
    try:
        info = stadium_goods.get_prices(name)
        await embed.send_listing(info, ctx, False)
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
