from services.concorrente_site.base import ProductPrice, SiteFetcher


class PremocilFetcher(SiteFetcher):
    def fetch_by_gtin(self, gtin: str) -> ProductPrice | None:
        return None
