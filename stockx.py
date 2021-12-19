import requests
import json
import re

import errors
import products

# scrape stockx and return a json
def scrape(keywords) -> json:
    json_string = json.dumps({"params": f"query={keywords}&hitsPerPage=20&facets=*"})
    byte_payload = bytes(json_string, "utf-8")
    algolia = {
        "x-algolia-agent": "Algolia for vanilla JavaScript 3.32.0",
        "x-algolia-application-id": "XW7SBCT9V6",
        "x-algolia-api-key": get_api_key(),
    }
    with requests.Session() as session:
        r = session.post(
            "https://xw7sbct9v6-dsn.algolia.net/1/indexes/products/query",
            params=algolia,
            verify=True,
            data=byte_payload,
            timeout=30,
        )
        return r.json()


def get_api_key() -> str:
    header = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate",
        "accept-language": "en-US,en;q=0.9,lt;q=0.8",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
    }
    stock_page = requests.get("https://stockx.com/", verify=True, headers=header).text
    script = re.findall(r"window.searchOnlyApiKey = .*", stock_page)
    if len(script) != 0:
        script = script[0].replace("window.searchOnlyApiKey = ", "")
        script = script.rstrip(script[-1]).strip("'")
        return script


def get_prices(name):
    keywords = name.replace(" ", "%20")
    result = scrape(keywords)

    if len(result["hits"]) == 0:
        raise errors.NoProductsFound

    product_url = result["hits"][0]["url"]

    apiurl = f"https://stockx.com/api/products/{product_url}?includes=market,360&currency=USD&country=US"

    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "accept-encoding": "gzip, deflate",
        "referer": f"https://stockx.com/{product_url}",
    }

    response = requests.get(apiurl, verify=True, headers=header)
    if response.status_code == 403:
        raise errors.SiteUnreachable

    response = response.json()
    general = response["Product"]

    product = products.Product(
        title=general["title"],
        url=f"https://stockx.com/{general['urlKey']}",
        thumbnail=general["media"]["thumbUrl"],
        color=0x099F5F,
        footer_text="StockX",
        footer_image="https://cdn.discordapp.com/attachments/734938642790744097/771078700178866226/stockx.png",
        processing_fee=3.0,
        asks_and_bids=True,
        category=general["contentGroup"],
    )
    product.add_seller_fee(9.5)
    product.add_seller_fee(9.0)
    product.add_seller_fee(8.5)
    product.add_seller_fee(8.0)

    for child in general["children"]:
        current_size = general["children"][child]
        if current_size["shoeSize"] == "15":
            break

        product.set_prices(
            size=current_size["shoeSize"],
            ask=current_size["market"]["lowestAsk"],
            bid=current_size["market"]["highestBid"],
        )

    if product.get_category() == "sneakers":
        if "styleId" in general:
            product.set_sku(general["styleId"])
        if "retailPrice" in general:
            product.set_retail_price(general["retailPrice"])
    elif product.get_category() == "streetwear-clothing":
        retail_price = next(
            (item for item in general["traits"] if item["name"] == "Retail"), None
        )
        if retail_price:
            product.set_retail_price(retail_price["value"])
    elif (
        product.get_category() == "collectibles" or product.get_category() == "handbags"
    ):
        retail_price = next(
            (item for item in general["traits"] if item["name"] == "Retail"), None
        )
        product.set_one_size()
        if retail_price:
            product.set_retail_price(retail_price["value"])
    else:
        raise errors.ProductNotSupported

    return product