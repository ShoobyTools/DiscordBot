import discord
import json
import requests
import asyncio
from dotenv import load_dotenv
import os

selected = 0
numResults = 0


def lookup_stockx(selection, keywords):
    json_string = json.dumps({"params": f"query={keywords}&hitsPerPage=20&facets=*"})
    byte_payload = bytes(json_string, "utf-8")
    algolia = {
        "x-algolia-agent": "Algolia for vanilla JavaScript 3.32.0",
        "x-algolia-application-id": "XW7SBCT9V6",
        "x-algolia-api-key": "6bfb5abee4dcd8cea8f0ca1ca085c2b3",
    }
    header = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9,ja-JP;q=0.8,ja;q=0.7,la;q=0.6",
        "appos": "web",
        "appversion": "0.1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
    }
    with requests.Session() as session:
        r = session.post(
            "https://xw7sbct9v6-dsn.algolia.net/1/indexes/products/query",
            params=algolia,
            verify=False,
            data=byte_payload,
            timeout=30,
        )
        results = r.json()["hits"][selection]
        apiurl = f"https://stockx.com/api/products/{results['url']}?includes=market,360&currency=USD"

    response = requests.get(apiurl, verify=False, headers=header)
    prices = response.json()
    general = prices["Product"]
    sizes = prices["Product"]["children"]


def s(ctx, *args):
    keywords = ""
    for word in args:
        keywords += word + "%20"
    json_string = json.dumps({"params": f"query={keywords}&hitsPerPage=20&facets=*"})
    byte_payload = bytes(json_string, "utf-8")
    params = {
        "x-algolia-agent": "Algolia for vanilla JavaScript 3.32.0",
        "x-algolia-application-id": "XW7SBCT9V6",
        "x-algolia-api-key": "6bfb5abee4dcd8cea8f0ca1ca085c2b3",
    }
    # used to get items using algolia api and get result
    # stockx changed something so now they use a different method
    # check website to see what requests are made when searching for product
    with requests.Session() as session:
        r = session.post(
            "https://xw7sbct9v6-dsn.algolia.net/1/indexes/products/query",
            params=params,
            verify=False,
            data=byte_payload,
            timeout=30,
        )
        numResults = len(r.json()["hits"])

    if numResults != 0:
        await lookup_stockx(0, keywords, ctx)
    else:
        print("No products found. Please try again.")
