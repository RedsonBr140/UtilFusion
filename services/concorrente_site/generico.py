from services.concorrente_site.base import ProductPrice, SiteFetcher


class GenericoFetcher(SiteFetcher):
    def __init__(self, *args, **kwargs):
        pass

    def fetch_by_name(self, descricao: str, gtin: str | None = None) -> ProductPrice | None:
        return None