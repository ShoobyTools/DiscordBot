from logging import error


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

# DEX stuff
class NoTokenFound(Error):
    pass

class Unsupported(Error):
    pass