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

    with open("data.json", "w", encoding="utf-8") as f:
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
    embed.add_field(name="⠀", value="⠀", inline=True)
    if "retailPrice" in general:
        embed.add_field(
            name="Retail Price:", value=f"${general['retailPrice']}", inline=True
        )
    else:
        embed.add_field(name="Retail Price:", value="N/A", inline=True)
    all_sizes = general["children"]
    for size in all_sizes:
        embed.add_field(
            name=all_sizes[size]["shoeSize"],
            value=f"```bash\nAsk: ${all_sizes[size]['market']['lowestAsk']}\nBid: ${all_sizes[size]['market']['highestBid']}```",
            inline=True,
        )
    embed.set_footer(
        text="StockX",
        icon_url="https://cdn.discordapp.com/attachments/734938642790744097/771078700178866226/stockx.png",
    )
    await ctx.send(embed=embed)
