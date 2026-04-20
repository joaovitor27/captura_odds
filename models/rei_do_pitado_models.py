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
    competicao: str
    partida: str
    data: str
    hora: str


@dataclass
class ResultadoFinalMarket(BaseMarket):
    """Estrutura específica do mercado Resultado."""
    time_casa: str
    time_fora: str
    odd_time_casa: float
    odd_time_fora: float
    odd_empate: float
    is_pagamento_antecipado: bool
