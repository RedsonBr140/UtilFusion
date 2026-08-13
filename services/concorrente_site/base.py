from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ProductPrice:
    descricao: str
    preco: float | None
    fonte: str = ""


class SiteFetcher(ABC):
    @abstractmethod
    def fetch_by_name(self, descricao: str, gtin: str | None = None) -> ProductPrice | None:
        raise NotImplementedError