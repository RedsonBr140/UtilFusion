from services.concorrente_site.base import SiteFetcher
from services.concorrente_site.generico import GenericoFetcher
from services.concorrente_site.premocil import PremocilFetcher

_FETCHERS: dict[str, type[SiteFetcher]] = {
    "Generico": GenericoFetcher,
    "Premocil": PremocilFetcher,
}


def get_fetcher(tipo: str) -> SiteFetcher:
    cls = _FETCHERS.get(tipo)
    if cls is None:
        raise ValueError(f"Tipo de concorrente nao suportado: {tipo}")
    return cls()


def available_tipos() -> list[str]:
    return sorted(_FETCHERS.keys())
