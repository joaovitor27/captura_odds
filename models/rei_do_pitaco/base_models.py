from dataclasses import dataclass, field
from typing import List


@dataclass
class Match:
    home_team: str
    away_team: str
    datetime: str


@dataclass
class Competition:
    name: str
    url: str = ""
    matches: List[Match] = field(default_factory=list)


@dataclass
class Category:
    name: str
    competitions: List[Competition] = field(default_factory=list)


@dataclass
class BaseMarket:
    """Estrutura obrigatória para qualquer mercado mapeado."""
    data: str
    hora: str
    competicao: str
    partida: str
