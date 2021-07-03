class Error(Exception):
    pass

class NoProductsFound(Error):
    pass

class SiteUnreachable(Error):
    pass