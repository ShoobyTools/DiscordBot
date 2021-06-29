import requests
import json
import discord


# scrape goat and return a json
async def scrape(keywords) -> json:
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
    return r.json()


async def get_goat_prices(name, ctx):
    keywords = name.replace(" ", "%20")
    results = await scrape(keywords)

    if len(results["hits"]) == 0:
        await ctx.send("No products found. Please try again.")
        return

    header = {
        "accept-encoding": "gzip, deflate, br",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36",
    }

    results = results["hits"][0]

    apiurl_prices = f"https://www.goat.com/web-api/v1/product_variants?productTemplateId={results['slug']}"
    apiurl_general = (
        f"https://www.goat.com/web-api/v1/product_templates/{results['slug']}"
    )

    prices = requests.get(apiurl_prices, verify=True, headers=header)
    general = requests.get(apiurl_general, verify=True, headers=header)

    prices = prices.json()
    general = general.json()

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
    embed.add_field(name="⠀", value="⠀", inline=True)
    if "localizedSpecialDisplayPriceCents" in general:
        price = int(
            general["localizedSpecialDisplayPriceCents"]["amountUsdCents"] / 100
        )
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

    for size in sizes:
        lowestPrice = int(size["lowestPriceCents"]["amountUsdCents"] / 100)
        embed.add_field(
            name=size["size"],
            value=f"```bash\n${lowestPrice}```",
            inline=True,
        )
    embed.set_footer(
        text="Goat",
        icon_url="https://cdn.discordapp.com/attachments/734938642790744097/771077292881477632/goat.png",
    )
    await ctx.send(embed=embed)
