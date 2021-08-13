class Error(Exception):
    pass

class NoProductsFound(Error):
    pass

class SiteUnreachable(Error):
    pass

class NoRetailPrice(Error):
    pass

class ProductNotSupported(Error):
    pass