import discord
from discord_slash import SlashCommand
import json
import requests
import os
import re
import threading

TOKEN = os.environ["TOKEN"]
client = discord.Client(intents=discord.Intents.all())
slash = SlashCommand(client, sync_commands=True)

selected = 0
numResults = 0

guild_ids = [734938642790744094, 403314326871474186]

@client.event
async def on_ready():
    await client.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening, name="Mention me for help"
        )
    )
    get_api_key()

@client.event
async def on_message(message):
    if client.user.mentioned_in(message):
        embed=discord.Embed(title="Price Checker instructions", description="Type `/` before any command to use it.", color=0x0008ff)
        embed.add_field(name="StockX", value="Checks StockX for prices.", inline=False)
        embed.add_field(name="Goat", value="Checks Goat for prices.", inline=False)
        embed.add_field(name="Vars", value="Get Shopify variants and stock if a site has it loaded (i.e. ShoePalace)", inline=False)
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


# stockx api key changes every 5 min so get it before every call
def get_api_key():
    # run a timer in the background to get the api key every 5 minutes
    threading.Timer(300, get_api_key).start()
    header = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate",
        "accept-language": "en-US,en;q=0.9,lt;q=0.8",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
    }
    stock_page = requests.get("https://stockx.com/", verify=True, headers=header).text
    script = re.findall(r"window.globalConstants = .*", stock_page)

    if len(script) != 0:
        script = script[0].replace("window.globalConstants = ", "")
        script = script.rstrip(script[-1])
        script = json.loads(script)
        os.environ["API_KEY"] = script["search"]["SEARCH_ONLY_API_KEY"]


async def lookup_stockx(result, ctx):
    product_url = result["hits"][0]["url"]

    apiurl = f"https://stockx.com/api/products/{product_url}?includes=market,360&currency=USD&country=US"

    header = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate",
        "accept-language": "en-US,en;q=0.9,ja-JP;q=0.8,ja;q=0.7,la;q=0.6",
        "appos": "web",
        "appversion": "0.1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
    }
    response = requests.get(apiurl, verify=True, headers=header).json()
    general = response["Product"]

    embed = discord.Embed(
        title=general["title"],
        url=f"https://stockx.com/{general['urlKey']}",
        color=0x099F5F,
    )
    embed.set_thumbnail(url=general["media"]["thumbUrl"])
    if "styleId" in general:
        embed.add_field(name="SKU:", value=general["styleId"], inline=True)
    else:
        embed.add_field(name="SKU:", value="N/A", inline=True)
    if "retailPrice" in general:
        embed.add_field(
            name="Retail Price:", value=f"${general['retailPrice']}", inline=True
        )
    else:
        embed.add_field(name="Retail Price:", value="N/A")
    embed.add_field(name="‎⠀", value="⠀", inline=False)
    all_sizes = general["children"]
    for size in all_sizes:
        embed.add_field(
            name=all_sizes[size]["shoeSize"],
            value=f"Lowest Ask: ${all_sizes[size]['market']['lowestAsk']}\nHighest Bid: ${all_sizes[size]['market']['highestBid']}",
            inline=True,
        )
    embed.set_footer(
        text="StockX",
        icon_url="https://cdn.discordapp.com/attachments/734938642790744097/771078700178866226/stockx.png",
    )
    await ctx.send(embed=embed)


async def lookup_goat(keywords, ctx):
    json_string = json.dumps({"params": f"query={keywords}&hitsPerPage=20&facets=*"})
    byte_payload = bytes(json_string, "utf-8")
    algolia = {
        "x-algolia-agent": "Algolia for vanilla JavaScript 3.25.1",
        "x-algolia-application-id": "2FWOTDVM2O",
        "x-algolia-api-key": "ac96de6fef0e02bb95d433d8d5c7038a",
    }
    header = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9,lt;q=0.8",
        "appos": "web",
        "appversion": "0.1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36",
    }
    with requests.Session() as session:
        r = session.post(
            "https://2fwotdvm2o-dsn.algolia.net/1/indexes/product_variants_v2/query",
            params=algolia,
            verify=True,
            data=byte_payload,
            timeout=30,
        )
        results = r.json()["hits"][0]
        apiurl_prices = f"https://www.goat.com/web-api/v1/product_variants?productTemplateId={results['slug']}"
        apiurl_general = (
            f"https://www.goat.com/web-api/v1/product_templates/{results['slug']}"
        )

    response_prices = requests.get(apiurl_prices, verify=True, headers=header)
    response_general = requests.get(apiurl_general, verify=True, headers=header)

    prices = response_prices.json()
    general = response_general.json()
    sizes = []
    for size in prices:
        if (
            size["boxCondition"] == "good_condition"
            and size["shoeCondition"] == "new_no_defects"
        ):
            sizes.append(size)

    embed = discord.Embed(
        title=f"{general['name']}",
        url=f"https://www.goat.com/sneakers/{general['slug']}",
        color=0xFFFFFE,
    )
    embed.set_thumbnail(url=general["gridPictureUrl"])
    if "sku" in general:
        embed.add_field(name="SKU:", value=general["sku"], inline=True)
    else:
        embed.add_field(name="SKU:", value="N/A", inline=True)
    if "localizedSpecialDisplayPriceCents" in general:
        price = int(general['localizedSpecialDisplayPriceCents']['amountUsdCents'] / 100)
        if price == 0:
            price = "N/A"
        else:
            price = "$" + str(price)
        embed.add_field(
            name="Retail Price:",
            value=price,
            inline=True,
        )
    else:
        embed.add_field(name="Retail Price:", value="N/A")
    embed.add_field(name="‎⠀", value="⠀", inline=False)
    for size in sizes:
        lowestPrice = int(size["lowestPriceCents"]["amountUsdCents"] / 100)
        embed.add_field(
            name=size["size"],
            value=f"```${lowestPrice}```",
            inline=True,
        )
    embed.set_footer(
        text="Goat",
        icon_url="https://cdn.discordapp.com/attachments/734938642790744097/771077292881477632/goat.png",
    )
    await ctx.send(embed=embed)


async def shoepalace(url, ctx):
    sp_url = re.sub(r".variant=.*", "", url)
    response = requests.get(sp_url + ".json").json()
    product = response["product"]
    variants = product["variants"]
    title = re.sub(r" Limit One Per Customer", "", product["title"])
    embed = discord.Embed(
        title=title,
        url=sp_url,
        color=0x37B2FA,
    )

    all_sizes = "```"
    all_stock = "```md\n"
    all_variants = "```\n"
    total_stock = 0
    for variant in variants:
        if variant.get("inventory_quantity") is None:
            await ctx.send("Failed to get stock")
            return
        quantity = str(variant["inventory_quantity"]).replace("-", "")
        total_stock += int(quantity)
        if quantity == "0":
            quantity = "*"
        size = variant['option2']
        if not size:
            size = variant['option1']
        all_sizes += f"{size} \n"
        all_stock += f"{quantity} \n"
        all_variants += f"{variant['id']}\n"

    all_sizes += "```"
    all_stock += "```"
    all_variants += "```"

    embed.add_field(
        name="Sizes",
        value=all_sizes,
        inline=True,
    )
    embed.add_field(
        name="Stock",
        value=all_stock,
        inline=True,
    )
    embed.add_field(
        name="Variants",
        value=all_variants,
        inline=True,
    )
    embed.add_field(name="Total Stock", value=f"```{total_stock}```", inline=False)

    embed.set_footer(
        text="ShoePalace",
        icon_url="https://media.discordapp.net/attachments/734938642790744097/839648671620268032/shoepalace.png",
    )
    await ctx.send(embed=embed)


async def get_vars(url, ctx):
    shop_url = re.sub(r".variant=.*", "", url)
    response = requests.get(shop_url + ".json").json()
    product = response["product"]
    variants = product["variants"]
    title = re.sub(r" Limit One Per Customer", "", product["title"])
    embed = discord.Embed(
        title=title,
        url=shop_url,
        color=0xFC604C,
    )

    all_sizes = "```"
    all_variants = "```\n"
    for variant in variants:
        size = variant['option1']
        if not size:
            size = variant['option2']
        all_sizes += f"{size} \n"
        all_variants += f"{variant['id']}\n"

    all_sizes += "```"
    all_variants += "```"

    embed.add_field(
        name="Sizes",
        value=all_sizes,
        inline=True,
    )
    embed.add_field(
        name="Variants",
        value=all_variants,
        inline=True,
    )

    embed.set_footer(
        text="Shopify Variants"
    )
    await ctx.send(embed=embed)

@slash.slash(name="StockX", description="Check StockX prices", guild_ids=guild_ids)
async def _stockx(ctx, name: str):
    keywords = name.replace(" ", "%20")
    result = await scrape(keywords)
    numResults = len(result["hits"])

    if numResults != 0:
        await lookup_stockx(result, ctx)
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
        print(keywords)
        await lookup_goat(keywords, ctx)
    else:
        await ctx.send("No products found. Please try again.")

@slash.slash(name="Vars", description="Get Shopify variants", guild_ids=guild_ids)
async def _variants(ctx, link):
    if "www.shoepalace.com" in link:
        await shoepalace(link, ctx)
    else:
        await get_vars(link, ctx)

client.run(TOKEN)
