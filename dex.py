import requests
import errors

class Token:
    def __init__(self, name, address, price, image_url, pair):
        self.name = name
        self.address = address
        self.price = price
        self.image = image_url
        self.url = f"https://www.dextools.io/app/ether/pair-explorer/{pair}"

def check(identifier: str):
    if identifier.startswith("0x"):
        raise errors.Unsupported
    url = "https://www.dextools.io/chain-ethereum/api/pair/search"
    headers = {
        "accept": "application/json",
        "accept-encoding": "gzip, deflate, br",
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
    }
    data = { "s": identifier }
    resp = requests.get(url, headers=headers, json=data)
    if resp.status_code == 200:
        tokens = resp.json()
        if len(tokens) == 0:
            raise errors.NoTokenFound
        token_address = tokens[0]["info"]["address"]
        alt_resp = requests.get(f"https://api.coingecko.com/api/v3/coins/ethereum/contract/{token_address}")
        if alt_resp.status_code == 200:
            image = alt_resp.json()["image"]["small"]
        else:
            image = None
        return Token(
            name=tokens[0]["info"]["symbol"],
            address=token_address,
            price=tokens[0]["price"],
            image_url=image,
            pair=tokens[0]["id"]
        )
    else:
        print(resp.status_code)
        print(resp.text)
        raise errors.SiteUnreachable
