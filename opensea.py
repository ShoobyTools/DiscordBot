import requests
import errors

class Contract:
    def __init__(self, address, symbol, image_url):
        self.symbol = symbol
        self.url = f"https://etherscan.io/address/{address}"
        self.address = address
        self.image = image_url

def get_contract(keyword: str):
    if "https://opensea.io/collection/" not in keyword:
        raise errors.Unsupported
    url = f"https://api.opensea.io/api/v1/collection/{keyword.replace('https://opensea.io/collection/', '')}"

    resp = requests.get(url)
    if resp.status_code == 200:
        contract = resp.json()["collection"]["primary_asset_contracts"][0]
    else:
        raise errors.SiteUnreachable
    return Contract(
        address=contract["address"],
        symbol=contract["symbol"],
        image_url=contract["image_url"]
    )