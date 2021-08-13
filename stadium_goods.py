import requests
from bs4 import BeautifulSoup
import json

import errors
import products

def int_or_float(num):
    try:
        return int(num)
    except ValueError:
        return float(num)

def calculate_price(price, processing_fee, selling_fee) -> float:
    return round(price * ((100.00 - (processing_fee + selling_fee))/100), 2)

def get_prices(name):
    header = {
        "accept": "application/json",
        "content-type": "application/json",
        "accept-encoding": "gzip, deflate",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    }

    data = {
        "operationId": "sg-front/cached-a41eba558ae6325f072164477a24d3c2",
        "variables": {
            "categorySlug": "",
            "initialSearchQuery": name,
            "initialSort": "RELEVANCE",
            "includeUnavailableProducts": None,
            "filteringOnCategory": False,
            "filteringOnBrand": False,
            "filteringOnMensSizes": False,
            "filteringOnKidsSizes": False,
            "filteringOnWomensSizes": False,
            "filteringOnApparelSizes": False,
            "filteringOnGender": False,
            "filteringOnColor": False,
            "filteringOnPriceRange": False,
        },
        "locale": "USA_USD",
    }

    r = requests.post(
        "https://graphql.stadiumgoods.com/graphql",
        headers=header,
        verify=True,
        json=data,
    )

    data = r.json()
    if len(data["data"]["configurableProducts"]["edges"]) == 0:
        raise errors.NoProductsFound
    
    data = data["data"]["configurableProducts"]["edges"][0]["node"]


    product = products.Product(
        title=f"{data['name']} {data['nickname']}",
        url=data["pdpUrl"],
        thumbnail=data["smallImage"]["url"],
        color=0xFFA500,
        footer_text="Stadium Goods",
        footer_image="https://media.discordapp.net/attachments/734938642790744097/859866121033089064/sg.jpg",
        processing_fee=0.0,
        asks_and_bids=False,
    )
    product.add_seller_fee(20.0)

    product.set_sku(data["manufacturerSku"].replace(" ", "-"))

    header = {
        "user-agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response = requests.get(data["pdpUrl"], headers=header, verify=True)
    soup=BeautifulSoup(response.content, "html.parser")
    all_sizes = soup.find("div", {"class": "product-sizes__options"}).find_all("span", {"class" : "product-sizes__detail"})
    prices = []
    for option in all_sizes:
        size = int_or_float(option.find("span", {"class" :"product-sizes__size"}).text.replace("Y", "").replace("W", "").strip("\n"))
        if size == 15:
            break
        price = option.find("span", {"class" :"product-sizes__price"}).text.strip("\n")
        if "Notify me" in price:
            price = 0
        else:
            price = price.replace(".00", "")
            price = int(price.strip("$"))
        prices.append((size, price))
    
    prices.sort()

    for price in prices:
        size = str(price[0])
        price = price[1]

        product.set_prices(size, price)

    return product

