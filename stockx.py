import requests
import json
import discord


# scrape stockx and return a json
async def scrape(keywords) -> json:
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


async def get_stockx_prices(name, ctx):
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
        await ctx.send("Error accessing StockX site (ERROR 403)")
        return
    response = response.json()
    general = response["Product"]

    info = {
        "title": general["title"],
        "url": f"https://stockx.com/{general['urlKey']}",
        "thumbnail": general["media"]["thumbUrl"],
        "sku": "N/A",
        "retail_price": "N/A",
        "multiple_sizes": True,
        "sizes": general["children"],
    }

    product_type = general["contentGroup"]
    if product_type == "sneakers":
        if "styleId" in general:
            info["sku"] = general["styleId"]
        if "retailPrice" in general:
            info["retail_price"] = f"${general['retailPrice']}"
    elif product_type == "streetwear-clothing":
        retail_price = next(
            (item for item in general["traits"] if item["name"] == "Retail"), None
        )
        if retail_price:
            info["retail_price"] = f"${retail_price['value']}"
    elif product_type == "collectibles":
        retail_price = next(
            (item for item in general["traits"] if item["name"] == "Retail"), None
        )
        if retail_price:
            info["retail_price"] = f"${retail_price['value']}"
        info["multiple_sizes"] = False
        info["sizes"] = general["market"]

    await send_embed(info, ctx)


async def send_embed(info: dict, ctx):
    embed = discord.Embed(
        title=info["title"],
        url=info["url"],
        color=0x099F5F,
    )
    embed.set_thumbnail(url=info["thumbnail"])
    embed.add_field(name="SKU:", value=info["sku"], inline=True)
    embed.add_field(name="⠀", value="⠀", inline=True)
    embed.add_field(name="Retail Price:", value=info["retail_price"], inline=True)
    if info["multiple_sizes"]:
        for size in info["sizes"]:
            ask = info["sizes"][size]["market"]["lowestAsk"]
            bid = info["sizes"][size]["market"]["highestBid"]
            if ask == 0:
                ask = "N/A"
            else:
                ask = "$" + str(ask)
            if bid == 0:
                bid = "N/A"
            else:
                bid = "$" + str(bid)
            embed.add_field(
                name=info["sizes"][size]["shoeSize"],
                value=f"```bash\nAsk: {ask}\nBid: {bid}```",
                inline=True,
            )
    else:
        ask = info["sizes"]["lowestAsk"]
        bid = info["sizes"]["highestBid"]
        embed.add_field(
            name="Ask",
            value=f"```bash\n${ask}```",
            inline=True,
        )
        embed.add_field(
            name="Bid",
            value=f"```bash\n${bid}```",
            inline=True,
        )
    embed.set_footer(
        text="StockX",
        icon_url="https://cdn.discordapp.com/attachments/734938642790744097/771078700178866226/stockx.png",
    )
    await ctx.send(embed=embed)
