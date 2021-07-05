import requests
import json

import errors

# scrape goat and return a json
def scrape(keywords) -> json:
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

def calculate_price(price, processing_fee, selling_fee) -> float:
    return round(price * ((100.00 - (processing_fee + selling_fee))/100), 2)

def get_prices(name):
    keywords = name.replace(" ", "%20")
    results = scrape(keywords)

    if len(results["hits"]) == 0:
        raise errors.NoProductsFound

    header = {
        "accept-encoding": "gzip, deflate, br",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36",
    }

    results = results["hits"][0]

    apiurl_prices = f"https://www.goat.com/web-api/v1/product_variants?productTemplateId={results['slug']}"
    apiurl_general = (
        f"https://www.goat.com/web-api/v1/product_templates/{results['slug']}"
    )

    options = requests.get(apiurl_prices, verify=True, headers=header)
    general = requests.get(apiurl_general, verify=True, headers=header)

    options = options.json()
    general = general.json()


    seller_fees = {
            "processing fee": 2.9,
            0: 9.5
        }
    prices = {}
    info = {
        "title": general['name'],
        "url": f"https://www.goat.com/sneakers/{general['slug']}",
        "thumbnail": general["gridPictureUrl"],
        "sku": "N/A",
        "retail price": "N/A",
        "sizes": {
            "seller fees": seller_fees,
            "asks and bids": False,
            "one size": False,
            "prices": prices
        },
        "color": 0xFFFFFE,
        "footer text": "Goat",
        "footer image": "https://cdn.discordapp.com/attachments/734938642790744097/771077292881477632/goat.png"
    }
    for size in options:
        if (
            size["boxCondition"] == "good_condition"
            and size["shoeCondition"] == "new_no_defects"
        ):
            if size["size"] == 15:
                break
            lowest_price = int(size["lowestPriceCents"]["amountUsdCents"] / 100)

            size_info = {
                "listing": lowest_price,
                0: calculate_price(lowest_price, info["sizes"]["seller fees"]["processing fee"], info["sizes"]["seller fees"][0])
            }

            info["sizes"]["prices"][str(size["size"])] = size_info

    if "sku" in general:
        info["sku"]=general["sku"].replace(" ", "-")

    if "localizedSpecialDisplayPriceCents" in general:
        price = int(
            general["localizedSpecialDisplayPriceCents"]["amountUsdCents"] / 100
        )
        if price == 0:
            price = "N/A"
        else:
            price = "$" + str(price)
        info["retail price"] = price

    return info