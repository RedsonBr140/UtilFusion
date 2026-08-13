from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ProductPrice:
    descricao: str
    preco: float | None
    fonte: str = ""


class SiteFetcher(ABC):
    @abstractmethod
    def fetch_by_gtin(self, gtin: str) -> ProductPrice | None:
        raise NotImplementedError
