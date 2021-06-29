import threading
import requests
import json
import re
import discord
import os

# scrape stockx and return a json
async def scrape(keywords):
    json_string = json.dumps({"params": f"query={keywords}&hitsPerPage=20&facets=*"})
    byte_payload = bytes(json_string, "utf-8")
    algolia = {
        "x-algolia-agent": "Algolia for vanilla JavaScript 3.32.0",
        "x-algolia-application-id": "XW7SBCT9V6",
        "x-algolia-api-key": "ZGRhZGYwNzIxMjJkNTgzMTc4OTNkYTRlZTkzNTlmMTRhNTViZDVmNTgzZWQyMDhkNWE1ZDA2YWE2OWZkOTM3NXZhbGlkVW50aWw9MTYyNTEwOTI4OQ==",
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


async def lookup_stockx(name, ctx):
    get_api_key()
    keywords = name.replace(" ", "%20")
    result = await scrape(keywords)

    if len(result["hits"]) == 0:
        await ctx.send("No products found. Please try again.")
        return

    product_url = result["hits"][0]["url"]

    apiurl = f"https://stockx.com/api/products/{product_url}?includes=market,360&currency=USD&country=US"

    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "accept-encoding": "gzip, deflate",
        "referer": f"https://stockx.com/{product_url}",
    }

    response = requests.get(apiurl, verify=True, headers=header)
    if response.status_code == 403:
        print("ACCESS DENIED")
        return
    response = response.json()
    general = response["Product"]

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(general, f, ensure_ascii=False, indent=4)

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