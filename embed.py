import discord
from discord import embeds
from discord import errors
from discord_slash.utils import manage_components
from discord_slash.model import ButtonStyle

import errors

stockx_price_buttons = [
    manage_components.create_button(
        style=ButtonStyle.green,
        label="Level 1",
        custom_id="stockx_profit_button1",
    ),
    manage_components.create_button(
        style=ButtonStyle.green,
        label="Level 2",
        custom_id="stockx_profit_button2",
    ),
    manage_components.create_button(
        style=ButtonStyle.green,
        label="Level 3",
        custom_id="stockx_profit_button3",
    ),
    manage_components.create_button(
        style=ButtonStyle.green,
        label="Level 4",
        custom_id="stockx_profit_button4",
    ),
    manage_components.create_button(
        style=ButtonStyle.grey,
        label="Listing",
        custom_id="stockx_listing_button",
    ),
]
stockx_button_row = manage_components.create_actionrow(*stockx_price_buttons)

goat_price_buttons = [
    manage_components.create_button(
        style=ButtonStyle.green, label="Profit", custom_id="goat_profit_button"
    ),
    manage_components.create_button(
        style=ButtonStyle.grey, label="Listing", custom_id="goat_listing_button"
    ),
]
goat_button_row = manage_components.create_actionrow(*goat_price_buttons)

sg_price_buttons = [
    manage_components.create_button(
        style=ButtonStyle.green, label="Profit", custom_id="sg_profit_button"
    ),
    manage_components.create_button(
        style=ButtonStyle.grey, label="Listing", custom_id="sg_listing_button"
    ),
]
sg_button_row = manage_components.create_actionrow(*sg_price_buttons)


async def send_listing(info: dict, ctx, editing: bool):
    embed = discord.Embed(
        title=info["title"],
        url=info["url"],
        color=info["color"],
    )
    embed.set_thumbnail(url=info["thumbnail"])
    embed.add_field(name="SKU:", value=info["sku"], inline=True)
    embed.add_field(name="⠀", value="⠀", inline=True)
    embed.add_field(name="Retail Price:", value=info["retail price"], inline=True)
    prices = info["sizes"]["prices"]
    # if the product has asks and bids for each size
    if info["sizes"]["asks and bids"]:
        # if the item has more than one size
        if not info["sizes"]["one size"]:
            for size in prices:
                ask = prices[size]["ask"]
                bid = prices[size]["bid"]
                embed.add_field(
                    name=size,
                    value=f"```bash\nAsk: {ask['listing']}\nBid: {bid['listing']}```",
                    inline=True,
                )
        # if the item has only one size
        else:
            embed.add_field(
                name="Ask",
                value=f"```bash\n{prices['']['ask']['listing']}```",
                inline=True,
            )
            embed.add_field(
                name="Bid",
                value=f"```bash\n{prices['']['bid']['listing']}```",
                inline=True,
            )
    # if the item doesn't have asks and bids
    else:
        for size in prices:
            embed.add_field(
                name=size,
                value=f"```bash\n${prices[size]['listing']}```",
                inline=True,
            )
    embed.set_footer(
        text=info["footer text"],
        icon_url=info["footer image"],
    )
    if not editing:
        if info["footer text"] == "StockX":
            await ctx.send(embed=embed, components=[stockx_button_row])
        elif info["footer text"] == "Goat":
            await ctx.send(embed=embed, components=[goat_button_row])
        elif info["footer text"] == "Stadium Goods":
            await ctx.send(embed=embed, components=[sg_button_row])
    else:
        await ctx.edit_origin(embed=embed)


async def send_profit(info: dict, ctx, seller_level=0):
    # if the product has no retail price then you can't calculate profit
    if info["retail price"] == "N/A":
        raise errors.NoRetailPrice
    embed = discord.Embed(
        title=info["title"],
        url=info["url"],
        color=info["color"],
    )
    embed.set_thumbnail(url=info["thumbnail"])
    embed.add_field(name="SKU:", value=info["sku"], inline=True)
    embed.add_field(
        name="Fees",
        value=f"{info['sizes']['seller fees'][seller_level]}% + {info['sizes']['seller fees']['processing fee']}%",
        inline=True,
    )
    embed.add_field(name="Retail Price:", value=info["retail price"], inline=True)
    prices = info["sizes"]["prices"]
    # if the product has asks and bids for each size
    if info["sizes"]["asks and bids"]:
        # if the item has more than one size
        if not info["sizes"]["one size"]:
            for size in prices:
                ask = prices[size]["ask"]
                bid = prices[size]["bid"]
                retail = float(info["retail price"].strip("$"))
                ask = float(ask[seller_level].strip("$"))
                bid = float(bid[seller_level].strip("$"))
                ask = round(ask - retail, 2)
                bid = round(bid - retail, 2)
                if bid < 0:
                    bid = f"-${bid * -1}"
                else:
                    bid = "$" + str(bid)
                if ask < 0:
                    ask = f"-${ask * -1}"
                else:
                    ask = "$" + str(ask)
                embed.add_field(
                    name=size,
                    value=f"```cpp\nAsk: {ask}\nBid: {bid}```",
                    inline=True,
                )
        # if the item has only one size
        else:
            ask = prices[""]["ask"]
            bid = prices[""]["bid"]
            if info["retail price"] != "N/A":
                retail = float(info["retail price"].strip("$"))
                ask = float(ask[seller_level].strip("$"))
                bid = float(bid[seller_level].strip("$"))
                ask = round(ask - retail, 2)
                bid = round(bid - retail, 2)
                if bid < 0:
                    bid = f"-${bid * -1}"
                else:
                    bid = "$" + str(bid)
                if ask < 0:
                    ask = f"-${ask * -1}"
                else:
                    ask = "$" + str(ask)
            embed.add_field(
                name="Ask",
                value=f"```cpp\n{ask}```",
                inline=True,
            )
            embed.add_field(
                name="Bid",
                value=f"```cpp\n{bid}```",
                inline=True,
            )
    # if the item doesn't have asks and bids
    else:
        for size in prices:
            price = prices[size]
            retail = float(info["retail price"].strip("$"))
            price = float(price[seller_level])
            price = round(price - retail, 2)
            if price < 0:
                price = f"-${price * -1}"
            else:
                price = "$" + str(price)
            embed.add_field(
                name=size,
                value=f"```cpp\n{price}```",
                inline=True,
            )
    embed.set_footer(
        text=info["footer text"],
        icon_url=info["footer image"],
    )
    await ctx.edit_origin(embed=embed)
