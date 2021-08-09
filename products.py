class Product:
    def __init__(
        self,
        title: str,
        url: str,
        thumbnail: str,
        color,
        footer_text: str,
        footer_image: str,
        sku="N/A",
        retail_price="N/A",
    ) -> None:
        self.title = title
        self.url = url
        self.thumbnail = thumbnail
        self.color = color
        self.footer_text = footer_text
        self.footer_image = footer_image
        self.sku = sku
        self.retail_price = retail_price

    def set_fee(self, processing_fee: float, selling_fee: float, level: int):
        self.processing_fee = processing_fee
        self.selling_fee[level] = selling_fee

    def _calculate_payout(self, price) -> float:

        return round(price * ((100.00 - (self.processing_fees + selling_fee)) / 100), 2)
