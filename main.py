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

selected = 0
numResults = 0

guild_ids = [403314326871474186, 734938642790744094]


@client.event
async def on_ready():
    await client.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening, name="Mention me for help"
        )
    )
    stockx.get_api_key()

@client.event
async def on_message(message):
    if client.user.mentioned_in(message):
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
        await message.channel.send(embed=embed)


# scrape stockx and return a json
async def scrape(keywords):
    json_string = json.dumps({"params": f"query={keywords}&hitsPerPage=20&facets=*"})
    byte_payload = bytes(json_string, "utf-8")
    algolia = {
        "x-algolia-agent": "Algolia for vanilla JavaScript 3.32.0",
        "x-algolia-application-id": "XW7SBCT9V6",
        "x-algolia-api-key": os.environ["API_KEY"],
    }
    with requests.Session() as session:
        r = session.post(
            "https://xw7sbct9v6-dsn.algolia.net/1/indexes/products/query",
            params=algolia,
            verify=True,
            data=byte_payload,
            timeout=30,
        )
        return r.json()


@slash.slash(name="StockX", description="Check StockX prices", guild_ids=guild_ids)
async def _stockx(ctx, name: str):
    keywords = name.replace(" ", "%20")
    result = await scrape(keywords)
    numResults = len(result["hits"])

    if numResults != 0:
        await stockx.lookup_stockx(result, ctx)
    else:
        await ctx.send("No products found. Please try again.")


@slash.slash(name="Goat", description="Check Goat prices", guild_ids=guild_ids)
async def _goat(ctx, name: str):
    keywords = name.replace(" ", "%20")
    json_string = json.dumps({"params": f"query={keywords}&hitsPerPage=20&facets=*"})
    byte_payload = bytes(json_string, "utf-8")
    algolia = {
        "x-algolia-agent": "Algolia for vanilla JavaScript 3.25.1",
        "x-algolia-application-id": "2FWOTDVM2O",
        "x-algolia-api-key": "ac96de6fef0e02bb95d433d8d5c7038a",
    }
    with requests.Session() as session:
        r = session.post(
            "https://2fwotdvm2o-dsn.algolia.net/1/indexes/product_variants_v2/query",
            params=algolia,
            verify=True,
            data=byte_payload,
            timeout=30,
        )
        numResults = len(r.json()["hits"])

    if numResults != 0:
        await goat.lookup_goat(keywords, ctx)
    else:
        await ctx.send("No products found. Please try again.")


@slash.slash(name="Vars", description="Get Shopify variants", guild_ids=guild_ids)
async def _variants(ctx, link):
    if "www.shoepalace.com" in link:
        await variants.shoepalace(link, ctx)
    else:
        await variants.get_vars(link, ctx)


client.run(TOKEN)
