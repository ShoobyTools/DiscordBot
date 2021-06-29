import discord
from discord_slash import SlashCommand
import os
from dotenv import load_dotenv

import stockx
import goat
import variants


load_dotenv()

TOKEN = os.environ["TOKEN"]
GUILD_ID = [int(os.environ["GUILD_ID"])]
client = discord.Client(intents=discord.Intents.default())
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
    await ctx.send(embed=embed)


@slash.slash(name="StockX", description="Check StockX prices", guild_ids=GUILD_ID)
async def _stockx(ctx, name: str):
    await stockx.get_stockx_prices(name, ctx)


@slash.slash(name="Goat", description="Check Goat prices", guild_ids=GUILD_ID)
async def _goat(ctx, name: str):
    await goat.get_goat_prices(name, ctx)


@slash.slash(name="Vars", description="Get Shopify variants", guild_ids=GUILD_ID)
async def _variants(ctx, link):
    await variants.get_vars(link, ctx)


client.run(TOKEN)
