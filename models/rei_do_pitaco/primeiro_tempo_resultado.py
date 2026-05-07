from dataclasses import dataclass
from models.rei_do_pitaco.base_models import BaseMarket

@dataclass
class PrimeiroTempoResultadoMarket(BaseMarket):
    """Estrutura específica do mercado 1º Tempo - Resultado."""
    time_casa: str
    time_fora: str
    odd_time_casa: float
    odd_time_fora: float
    odd_empate: float
    is_pagamento_antecipado: bool
