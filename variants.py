import requests
import discord
import re


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
    embed.set_thumbnail(url=product["images"][0]["src"])
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
        size = variant["option2"]
        if not size:
            size = variant["option1"]
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
    title = product["title"].lower().title()
    title = re.sub(r" Limit One Per Customer", "", title)
    embed = discord.Embed(
        title=title,
        url=shop_url,
        color=0xFC604C,
    )
    embed.set_thumbnail(url=product["images"][0]["src"])
    all_sizes = "```"
    all_variants = "```\n"
    for variant in variants:
        size = variant["option1"]
        if not size:
            size = variant["option2"]
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

    embed.set_footer(text="Shopify Variants")
    await ctx.send(embed=embed)
