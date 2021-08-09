from discord.flags import SystemChannelFlags


class Product:
    def __init__(
        self,
        title: str,
        url: str,
        thumbnail: str,
        color,
        footer_text: str,
        footer_image: str,
        processing_fee: float,
        category=None,
    ) -> None:
        self._title = title
        self._url = url
        self._thumbnail = thumbnail
        self._color = color
        self._footer_text = footer_text
        self._footer_image = footer_image
        self._sku = None
        self._retail_price = None
        self._processing_fee = processing_fee
        self._selling_fees = []
        self._category = category
        self._sizes = {}

    def _calculate_payouts(self, price) -> list:
        all_level_payouts = []
        for fee in self._selling_fees:
            payout = price
            if price:
                payout = round(price * ((100.00 - (self._processing_fees + fee)) / 100), 2)

            all_level_payouts.append(payout)
        
        return all_level_payouts


    def _cleanup_size(size: str) -> str:
        return size.strip("W").strip("Y")

# ------------------------------------------------------------------------------
#  SETTERS
# ------------------------------------------------------------------------------
    def add_seller_fee(self, selling_fee: float) -> None:
        self._selling_fees.append(selling_fee)

    def set_sku(self, sku: str) -> None:
        self._sku = sku.replace(" ", "-")
    
    def set_retail_price(self, retail_price: int) -> None:
        self._retail_price = retail_price

    def set_ask(self, size: str, ask: int) -> None:
        _size = self._cleanup_size(size)
        if ask == 0:
            _ask = None
        else:
            _ask = ask
        self._sizes[_size]["ask"]["listing"] = _ask
        all_payouts = self._calculate_payouts(_ask)

        payouts = {}
        level = 1
        for payout in all_payouts:
            payouts[level] = payout
            level += 1
        
        self._sizes[_size]["ask"]["payouts"] = payouts


    def set_bid(self, size: str, bid: int) -> None:
        _size = self._cleanup_size(size)
        if bid == 0:
            _bid = None
        else:
            _bid = bid
        self._sizes[_size]["bid"]["listing"] = _bid
        all_payouts = self._calculate_payouts(_bid)

        payouts = {}
        level = 1
        for payout in all_payouts:
            payouts[level] = payout
            level += 1
        
        self._sizes[_size]["bid"]["payouts"] = payouts


# ------------------------------------------------------------------------------
#  GETTERS
# ------------------------------------------------------------------------------
    def get_title(self) -> str:
        return self._title

    def get_url(self) -> str:
        return self._url
    
    def get_thumbnail(self) -> str:
        return self._thumbnail
    
    def get_color(self):
        return self._color
    
    def get_footer_text(self) -> str:
        return self._footer_text
    
    def get_footer_image(self) -> str:
        return self._footer_image
    
    def get_sku(self) -> str:
        return self._sku
    
    def get_retail_price(self) -> int:
        return self._retail_price
    
    def get_category(self) -> str:
        return self._category