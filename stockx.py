import requests
import json
import re

import errors

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
    script = re.findall(r"window.globalConstants = .*", stock_page)
    if len(script) != 0:
        script = script[0].replace("window.globalConstants = ", "")
        script = script.rstrip(script[-1])
        script = json.loads(script)
        return script["search"]["SEARCH_ONLY_API_KEY"]

def calculate_price(price, processing_fee, selling_fee) -> float:
    return round(price * ((100.00 - (processing_fee + selling_fee))/100), 2)

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

    seller_fees = {
                "processing fee": 3.0,
                1: 9.5,
                2: 9.0,
                3: 8.5,
                4: 8.0
            }
    prices = {}
    for child in general["children"]:
        current_size = general["children"][child]
        if current_size["shoeSize"] == "15":
            break
        ask = current_size["market"]["lowestAsk"]
        bid = current_size["market"]["highestBid"]
        if ask == 0:
            ask = "N/A"
        else:
            ask_profit_level1 = f"${calculate_price(ask, seller_fees['processing fee'], seller_fees[1])}"
            ask_profit_level2 = f"${calculate_price(ask, seller_fees['processing fee'], seller_fees[2])}"
            ask_profit_level3 = f"${calculate_price(ask, seller_fees['processing fee'], seller_fees[3])}"
            ask_profit_level4 = f"${calculate_price(ask, seller_fees['processing fee'], seller_fees[4])}"
            ask = "$" + str(ask)
        if bid == 0:
            bid = "N/A"
            ask_profit_level1 = "N/A"
            ask_profit_level2 = "N/A"
            ask_profit_level3 = "N/A"
            ask_profit_level4 = "N/A"
        else:
            bid_profit_level1 = f"${calculate_price(bid, seller_fees['processing fee'], seller_fees[1])}"
            bid_profit_level2 = f"${calculate_price(bid, seller_fees['processing fee'], seller_fees[2])}"
            bid_profit_level3 = f"${calculate_price(bid, seller_fees['processing fee'], seller_fees[3])}"
            bid_profit_level4 = f"${calculate_price(bid, seller_fees['processing fee'], seller_fees[4])}"
            bid = "$" + str(bid)
        
        ask_info = {
            "listing": ask,
            1: ask_profit_level1,
            2: ask_profit_level2,
            3: ask_profit_level3,
            4: ask_profit_level4
        }

        bid_info = {
            "listing": bid,
            1: bid_profit_level1,
            2: bid_profit_level2,
            3: bid_profit_level3,
            4: bid_profit_level4
        }
        prices[current_size["shoeSize"]] = {
            "ask": ask_info,
            "bid": bid_info
        }
    info = {
        "title": general["title"],
        "url": f"https://stockx.com/{general['urlKey']}",
        "thumbnail": general["media"]["thumbUrl"],
        "sku": "N/A",
        "retail price": "N/A",
        "sizes": {
            "seller fees": seller_fees,
            "asks and bids": True,
            "one size": False,
            "prices": prices
        },
        "color": 0x099F5F,
        "footer text": "StockX",
        "footer image": "https://cdn.discordapp.com/attachments/734938642790744097/771078700178866226/stockx.png"
    }

    product_type = general["contentGroup"]
    if product_type == "sneakers":
        if "styleId" in general:
            info["sku"] = general["styleId"]
        if "retailPrice" in general:
            info["retail price"] = f"${general['retailPrice']}"
    elif product_type == "streetwear-clothing":
        retail_price = next(
            (item for item in general["traits"] if item["name"] == "Retail"), None
        )
        if retail_price:
            info["retail price"] = f"${retail_price['value']}"
    elif product_type == "collectibles":
        retail_price = next(
            (item for item in general["traits"] if item["name"] == "Retail"), None
        )
        if retail_price:
            info["retail price"] = f"${retail_price['value']}"
        info["sizes"]["one size"] = True
    
    return info