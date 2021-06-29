import discord
from discord_slash import SlashCommand
import json
import requests
import os
from dotenv import load_dotenv

import stockx
import goat
import variants

load_dotenv()

TOKEN = os.environ["TOKEN"]
client = discord.Client(intents=discord.Intents.default())
slash = SlashCommand(client, sync_commands=True)

guild_ids = [403314326871474186, 734938642790744094]

@client.event
async def on_ready():
    await client.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening, name="Type /info for help"
        )
    )

@slash.slash(name="Info", description="Provides help on price checker commands", guild_ids=guild_ids)
async def _help(ctx):
    embed = discord.Embed(
        title="Price Checker instructions",
        description="Type `/` before any command to use it.",
        color=0x0008FF,
    )
    embed.add_field(name="StockX", value="Checks StockX for prices.", inline=False)
    embed.add_field(name="Goat", value="Checks Goat for prices.", inline=False)
    embed.add_field(
        name="Vars",
        value="Get Shopify variants and stock if a site has it loaded (i.e. ShoePalace)",
        inline=False,
    )
    await ctx.send(embed=embed)


@slash.slash(name="StockX", description="Check StockX prices", guild_ids=guild_ids)
async def _stockx(ctx, name: str):
    await stockx.lookup_stockx(name, ctx)


@slash.slash(name="Goat", description="Check Goat prices", guild_ids=guild_ids)
async def _goat(ctx, name: str):
    goat.lookup_goat(name, ctx)


@slash.slash(name="Vars", description="Get Shopify variants", guild_ids=guild_ids)
async def _variants(ctx, link):
    variants.get_vars(link, ctx)

client.run(TOKEN)
