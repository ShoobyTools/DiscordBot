import discord

import errors

async def send_listing(info, ctx):
    embed = discord.Embed(
        title=info["title"],
        url=info["url"],
        color=info["color"],
    )
    embed.set_thumbnail(url=info["image"])
    embed.add_field(name="SKU:", value=info["sku"], inline=True)
    embed.add_field(name="⠀", value="⠀", inline=True)
    embed.add_field(name="Retail Price:", value=f"${info['retailPrice']}", inline=True)
    for variant in info["variants"]:
        ask = variant["ask"]
        bid = variant["bid"]
        if ask:
            ask = f"${ask}"
        else:
            ask = "N/A"
        if bid:
            bid = f"${bid}"
        else:
            bid = "N/A"
        embed.add_field(
            name=variant["size"],
            value=f"```bash\nAsk: {ask}\nBid: {bid}```",
            inline=True,
        )
    print(info["footerText"])
    embed.set_footer(
        text=info["footerText"],
        icon_url=info["footerImage"],
    )
    await ctx.send(embed=embed)

async def send_gas(ctx, costs):
    embed = discord.Embed(title="TX ETH Costs", color=0x006097)
    embed.add_field(
        name="Info",
        value=f"```cpp\nPrice Per: {costs[0].price}\nNumber of NFTs: {costs[0].num}\nGas limit: {costs[0].limit}\n{costs[0].utilization * 100}% Utilization: {costs[0].limit * costs[0].utilization}```",
        inline=False
    )
    gas = "```\n"
    utilization_totals = "```\n"
    max_totals = "```\n"
    utilization_averages = "```\n"
    max_averages = "```\n"
    for cost in costs:
        gas += str(cost.gas) + "\n"
        utilization_totals += str(cost.utilization_total) + "\n"
        max_totals += str(cost.max_total) + "\n"
        utilization_averages += str(cost.utilization_average) + "\n"
        max_averages += str(cost.max_average) + "\n"
    gas += "```"
    utilization_totals += "```"
    max_totals += "```"
    utilization_averages += "```"
    max_averages += "```"
    embed.add_field(name="Gas Price (GWEI)", value=gas, inline=True)
    embed.add_field(name="Total (ETH)", value=max_totals, inline=True)
    embed.add_field(name="Average (ETH)", value=max_averages, inline=True)

    embed.add_field(name="Utilization", value=f"`{costs[0].utilization * 100}%`", inline=False)

    embed.add_field(name="Gas Price (GWEI)", value=gas, inline=True)
    embed.add_field(name="Total (ETH)", value=utilization_totals, inline=True)
    embed.add_field(name="Average (ETH)", value=utilization_averages, inline=True)
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

async def send_contract(ctx, contract):
    embed = discord.Embed(title=contract.symbol ,color=0x6699CC)
    embed.set_thumbnail(url=contract.image)
    embed.add_field(
        name="Contract",
        value=f"Address: ```cpp\n{contract.address}```[Etherscan]({contract.url})\n[Moby](https://moby.gg/collection/{contract.address})",
        inline=True
    )

    await ctx.send(embed=embed)