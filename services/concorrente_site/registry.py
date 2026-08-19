from services.concorrente_site.base import SiteFetcher
from services.concorrente_site.generico import GenericoFetcher
from services.concorrente_site.premocil import PremocilFetcher
from services.concorrente_site.tupan import TupanFetcher

_FETCHERS: dict[str, type[SiteFetcher]] = {
    "Generico": GenericoFetcher,
    "Premocil": PremocilFetcher,
    "Tupan": TupanFetcher,
}


def get_fetcher(tipo: str, **kwargs) -> SiteFetcher:
    cls = _FETCHERS.get(tipo)
    if cls is None:
        raise ValueError(f"Tipo de concorrente nao suportado: {tipo}")
    return cls(**kwargs)


def available_tipos() -> list[str]:
    return sorted(_FETCHERS.keys())
