from discord import errors
import stockx
import goat
import numpy
import discord

def int_or_float(num):
    try:
        return int(num)
    except ValueError:
        return float(num)

async def get_prices(name, ctx):
    try:
        stockx_info = stockx.get_prices(name)
    except errors.NoProductsFound:
        await ctx.send("Product not found on StockX.")
    try:
        goat_info = goat.get_prices(stockx_info["sku"])
    except errors.NoProductsFound:
        await ctx.send("Product not found on Goat.")

    stockx_prices = stockx_info["sizes"]["prices"]
    goat_prices = goat_info["sizes"]["prices"]

    stockx_min = next(iter(stockx_prices))
    goat_min = next(iter(goat_prices))
    
    stockx_max = next(iter(reversed(stockx_prices)))
    goat_max = next(iter(reversed(goat_prices)))
    
    min_size = min(int_or_float(stockx_min), int_or_float(goat_min))

    max_size = max(int_or_float(stockx_max), int_or_float(goat_max))

    size_list = "```"
    stockx_list = "```bash"
    goat_list = "```bash"

    size_range = numpy.arange(min_size, max_size + 0.5, 0.5)
    for size in size_range:
        # size = int_or_float(size)
        size_name = str(size).replace('.0', '')
        size_list += f"\n{size_name}"

        if size_name in stockx_prices:
            stockx_list += f"\n{stockx_prices[size_name]['bid']['listing']}"
        else:
            stockx_list += f"\nN/A"
        
        if size_name in goat_prices:
            goat_list += f"\n${goat_prices[size_name]['listing']}"
        else:
            goat_list += f"\nN/A"
        
        size_list += "\n----"
        stockx_list += "\n----"
        goat_list += "\n----"

    size_list += "```"
    stockx_list += "```"
    goat_list += "```"

    embed = discord.Embed(
        title="Comparison",
        color=0xFF69B4,
    )
    embed.set_thumbnail(url=goat_info["thumbnail"])
    embed.add_field(name="SKU:", value=stockx_info["sku"], inline=True)
    embed.add_field(name="⠀", value="⠀", inline=True)
    embed.add_field(name="Retail Price:", value=stockx_info["retail price"], inline=True)
    
    embed.add_field(name="Sizes:", value=size_list, inline=True)
    embed.add_field(name="StockX:", value=stockx_list, inline=True)
    embed.add_field(name="Goat:", value=goat_list, inline=True)
    embed.set_footer(
        text="StockX vs Goat",
    )

    await ctx.send(embed=embed)
