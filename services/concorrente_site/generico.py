from services.concorrente_site.base import ProductPrice, SiteFetcher


class GenericoFetcher(SiteFetcher):
    def fetch_by_gtin(self, gtin: str) -> ProductPrice | None:
        return None
