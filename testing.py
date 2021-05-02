import discord
import json
import requests
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = str(os.environ.get(API_KEY))

selected = 0
numResults = 0

# scrape stockx and return a json
def scrape(keywords):
    json_string = json.dumps({"params": f"query={keywords}&hitsPerPage=20&facets=*"})
    byte_payload = bytes(json_string, "utf-8")
    algolia = {
        "x-algolia-agent": "Algolia for vanilla JavaScript 3.32.0",
        "x-algolia-application-id": "XW7SBCT9V6",
        "x-algolia-api-key": API_KEY,
    }
    with requests.Session() as session:
        r = session.post(
            "https://xw7sbct9v6-dsn.algolia.net/1/indexes/products/query",
            params=algolia,
            verify=False,
            data=byte_payload,
            timeout=30,
        )
        return r.json()


def lookup_stockx(result):
    product_url = result["hits"][0]["url"]

    apiurl = f"https://stockx.com/api/products/{product_url}?includes=market,360&currency=USD&country=US"

    header = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate",
        "accept-language": "en-US,en;q=0.9,ja-JP;q=0.8,ja;q=0.7,la;q=0.6",
        "appos": "web",
        "appversion": "0.1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
    }
    response = requests.get(apiurl, verify=True, headers=header).json()
    print_to_json(response)


def s(keywords):
    keywords.replace(" ", "%")
    result = scrape(keywords)
    print_to_json(result)
    numResults = len(result["hits"])

    if numResults != 0:
        lookup_stockx(result)
    else:
        print("No products found. Please try again.")


def print_to_json(data):
    with open("results.json", "w") as ouput:
        json.dump(data, ouput)


input = "jordan 5 raging bull"
s(input)
