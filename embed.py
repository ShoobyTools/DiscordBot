import discord
from discord import errors
from discord_slash.utils import manage_components
from discord_slash.model import ButtonStyle

import errors
import products

stockx_price_buttons = [
    manage_components.create_button(
        style=ButtonStyle.green,
        label="Level 1",
        custom_id="stockx_payout_button1",
    ),
    manage_components.create_button(
        style=ButtonStyle.green,
        label="Level 2",
        custom_id="stockx_payout_button2",
    ),
    manage_components.create_button(
        style=ButtonStyle.green,
        label="Level 3",
        custom_id="stockx_payout_button3",
    ),
    manage_components.create_button(
        style=ButtonStyle.green,
        label="Level 4",
        custom_id="stockx_payout_button4",
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
        style=ButtonStyle.green, label="Payout", custom_id="goat_payout_button"
    ),
    manage_components.create_button(
        style=ButtonStyle.grey, label="Listing", custom_id="goat_listing_button"
    ),
]
goat_button_row = manage_components.create_actionrow(*goat_price_buttons)

sg_price_buttons = [
    manage_components.create_button(
        style=ButtonStyle.green, label="Payout", custom_id="sg_payout_button"
    ),
    manage_components.create_button(
        style=ButtonStyle.grey, label="Listing", custom_id="sg_listing_button"
    ),
]
sg_button_row = manage_components.create_actionrow(*sg_price_buttons)


async def send_listing(product: products.Product, ctx, editing: bool):
    embed = discord.Embed(
        title=product.get_title(),
        url=product.get_url(),
        color=product.get_color(),
    )
    embed.set_thumbnail(url=product.get_thumbnail())
    embed.add_field(name="SKU:", value=product.get_sku(), inline=True)
    embed.add_field(name="⠀", value="⠀", inline=True)
    embed.add_field(name="Retail Price:", value=product.get_retail_price(), inline=True)
    prices = product.get_prices()
    # if the product has asks and bids for each size
    if product.asks_and_bids():
        # if the item has more than one size
        if not product.one_size():
            for size in prices:
                ask = prices[size]["ask"]["listing"]
                bid = prices[size]["bid"]["listing"]
                if ask:
                    ask = f"${ask}"
                if bid:
                    bid = f"${bid}"
                embed.add_field(
                    name=size,
                    value=f"```bash\nAsk: {ask}\nBid: {bid}```",
                    inline=True,
                )
        # if the item has only one size
        else:
            ask = prices[""]["ask"]["listing"]
            bid = prices[""]["bid"]["listing"]
            if ask:
                ask = f"${ask}"
            if bid:
                bid = f"${bid}"
            embed.add_field(
                name="Ask",
                value=f"```bash\n{ask}```",
                inline=True,
            )
            embed.add_field(
                name="Bid",
                value=f"```bash\n{bid}```",
                inline=True,
            )
    # if the item doesn't have asks and bids
    else:
        for size in prices:
            listing = prices[size]["listing"]
            if listing:
                listing = f"${listing}"
            embed.add_field(
                name=size,
                value=f"```bash\n{listing}```",
                inline=True,
            )
    embed.set_footer(
        text=product.get_footer_text(),
        icon_url=product.get_footer_image(),
    )

    if not editing:
        if product.get_footer_text() == "StockX":
            await ctx.send(embed=embed, components=[stockx_button_row])
        elif product.get_footer_text() == "Goat":
            await ctx.send(embed=embed, components=[goat_button_row])
        elif product.get_footer_text() == "Stadium Goods":
            await ctx.send(embed=embed, components=[sg_button_row])
    else:
        await ctx.edit_origin(embed=embed)


async def send_payout(product: products.Product, ctx, seller_level=1):
    # if the product has no retail price then you can't calculate profit
    if product.get_retail_price() == "N/A":
        raise errors.NoRetailPrice
    embed = discord.Embed(
        title=product.get_title(),
        url=product.get_url(),
        color=product.get_color(),
    )
    embed.set_thumbnail(url=product.get_thumbnail())
    embed.add_field(name="SKU:", value=product.get_sku(), inline=True)
    embed.add_field(
        name="Fees",
        value=str(product.get_fees(seller_level)) + "%",
        inline=True,
    )
    embed.add_field(name="Retail Price:", value=product.get_retail_price(), inline=True)
    prices = product.get_prices()
    # if the product has asks and bids for each size
    if product.asks_and_bids():
        # if the item has more than one size
        if not product.one_size():
            for size in prices:
                ask = prices[size]["ask"]["payouts"][seller_level]
                bid = prices[size]["bid"]["payouts"][seller_level]
                if ask:
                    ask = f"${ask}"
                if bid:
                    bid = f"${bid}"
                embed.add_field(
                    name=size,
                    value=f"```cpp\nAsk: {ask}\nBid: {bid}```",
                    inline=True,
                )
        # if the item has only one size
        else:
            ask = prices[""]["ask"]["payouts"][seller_level]
            bid = prices[""]["bid"]["payouts"][seller_level]
            if ask:
                ask = f"${ask}"
            if bid:
                bid = f"${bid}"
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
            listing = prices[size]["payouts"][seller_level]
            if listing:
                listing = f"${listing}"
            embed.add_field(
                name=size,
                value=f"```cpp\n{listing}```",
                inline=True,
            )
    embed.set_footer(
        text=product.get_footer_text(),
        icon_url=product.get_footer_image(),
    )
    await ctx.edit_origin(embed=embed)


async def send_gas(ctx, costs):
    embed = discord.Embed(title="Max ETH Costs", color=0x006097)
    embed.add_field(
        name="Info",
        value=f"```cpp\nPrice Per: {costs[0].price}\nNumber of NFTs: {costs[0].num}\nGas limit: {costs[0].limit}```",
        inline=False
    )
    gas = "```\n"
    totals = "```\n"
    averages = "```\n"
    for cost in costs:
        gas += str(cost.gas) + "\n"
        totals += str(cost.total) + "\n"
        averages += str(cost.average) + "\n"
    gas += "```"
    totals += "```"
    averages += "```"
    embed.add_field(name="Gas Price (GWEI)", value=gas, inline=True)
    embed.add_field(name="Total (ETH)", value=totals, inline=True)
    embed.add_field(name="Average (ETH)", value=averages, inline=True)

    await ctx.send(embed=embed)

async def send_token(ctx, token):
    embed = discord.Embed(title=token.name, url=token.url ,color=0x86DC3D)
    if token.image:
        embed.set_thumbnail(url=token.image)
    embed.add_field(
        name="Info",
        value=f"```cpp\nAdress: {token.address}\nPrice: ${token.price:.20f}```",
        inline=True
    )

    await ctx.send(embed=embed)