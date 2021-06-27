import threading
import requests
import json
import re
import discord
import os

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
