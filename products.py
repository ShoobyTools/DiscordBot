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
        asks_and_bids: bool,
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
        self._asks_and_bids = asks_and_bids
        self._one_size = False
        self._processing_fee = processing_fee
        self._selling_fees = []
        self._category = category
        self._sizes = {}

    def _calculate_payouts(self, price) -> list:
        all_level_payouts = []
        for fee in self._selling_fees:
            payout = price
            if price:
                payout = round(
                    price * ((100.00 - (self._processing_fee + fee)) / 100), 2
                )

            all_level_payouts.append(payout)

        return all_level_payouts

    def _cleanup_size(self, size: str) -> str:
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

    def set_one_size(self) -> None:
        self._one_size = True

    def set_prices(self, size: str, ask: int, bid=None) -> None:
        _size = self._cleanup_size(size)
        if ask == 0:
            _ask = None
        else:
            _ask = ask

        all_ask_payouts = self._calculate_payouts(_ask)

        ask_payouts = {}
        level = 1
        for payout in all_ask_payouts:
            ask_payouts[level] = payout
            level += 1

        if not self.asks_and_bids():
            size_info = {_size: {"listing": _ask, "payouts": ask_payouts}}
        else:
            if bid == 0:
                _bid = None
            else:
                _bid = bid

            all_bid_payouts = self._calculate_payouts(_bid)

            bid_payouts = {}
            level = 1
            for payout in all_bid_payouts:
                bid_payouts[level] = payout
                level += 1
            size_info = {
                _size: {
                    "ask": {"listing": _ask, "payouts": ask_payouts},
                    "bid": {"listing": _bid, "payouts": bid_payouts},
                }
            }

        self._sizes.update(size_info)

    # ------------------------------------------------------------------------------
    #  GETTERS
    # ------------------------------------------------------------------------------
    def get_prices(self) -> dict:
        return self._sizes

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
        if self._sku:
            return self._sku
        else:
            return "N/A"

    def get_retail_price(self) -> str:
        if self._retail_price:
            return f"${self._retail_price}"
        else:
            return "N/A"

    def asks_and_bids(self) -> bool:
        return self._asks_and_bids

    def one_size(self) -> bool:
        return self._one_size

    def get_category(self) -> str:
        return self._category
