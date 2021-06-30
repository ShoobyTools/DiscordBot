import requests
from bs4 import BeautifulSoup

import embed

def int_or_float(num):
    try:
        return int(num)
    except ValueError:
        return float(num)

def get_prices(name, ctx):
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
    data = data["data"]["configurableProducts"]["edges"][0]["node"]

    prices = {
        "asks_and_bids": False
    }
    info = {
        "title": f"{data['name']} {data['nickname']}",
        "url": data["pdpUrl"],
        "thumbnail": data["smallImage"]["url"],
        "sku": data["manufacturerSku"],
        "retail_price": "N/A",
        "multiple_sizes": True,
        "prices": prices,
    }

    header = {
        "user-agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(data["pdpUrl"], headers=header, verify=True)
    soup=BeautifulSoup(response.content, "html.parser")
    all_sizes = soup.find("div", {"class": "product-sizes__options"}).find_all("span", {"class" : "product-sizes__detail"})
    prices = []
    for option in all_sizes:
        size = int_or_float(option.find("span", {"class" :"product-sizes__size"}).text.strip("\n"))
        price = option.find("span", {"class" :"product-sizes__price"}).text.strip("\n")
        if "Notify me" in price:
            price = "N/A"
        else:
            price = price.replace(".00", "")
        prices.append((size, price))
    
    prices.sort()



get_prices("bodega 990", "test")
