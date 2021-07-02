import discord

async def send(info: dict, ctx):
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
    if info["sizes"]["asks and bids"]:
        if not info["sizes"]["one size"]:
            for size in prices:
                ask = prices[size]["ask"]
                bid = prices[size]["bid"]
                embed.add_field(
                    name=size,
                    value=f"```bash\nAsk: {ask}\nBid: {bid}```",
                    inline=True,
                )
        else:
            embed.add_field(
                name="Ask",
                value=f"```bash\n{prices['']['ask']}```",
                inline=True,
            )
            embed.add_field(
                name="Bid",
                value=f"```bash\n{prices['']['bid']}```",
                inline=True,
            )
    else:
        for size in prices:
            embed.add_field(
                name=size,
                value=f"```bash\n{prices[size]}```",
                inline=True,
            )
    embed.set_footer(
        text=info["footer text"],
        icon_url=info["footer image"],
    )
    await ctx.send(embed=embed)