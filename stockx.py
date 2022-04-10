import requests
import os
from dotenv import load_dotenv
load_dotenv()

def stockX(keywords):
    endpoint = "/stockx"
    params = { "keywords": keywords }
    resp = requests.get(os.environ["API_URL"] + endpoint, params=params)
    info = resp.json()
    info["color"] = 0x099F5F
    info["footerText"] = "StockX"
    info["footerImage"] ="https://cdn.discordapp.com/attachments/734938642790744097/771078700178866226/stockx.png"
    return info
