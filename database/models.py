from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    id: int
    username: str
    password_hash: str
    active: bool
    created_at: datetime | None = None


@dataclass
class Filial:
    id: int
    nome_fantasia: str
    endereco: str
    cidade: str
    estado: str
    telefone: str
    created_at: datetime | None = None
