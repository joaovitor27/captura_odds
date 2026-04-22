from dataclasses import dataclass

from models.rei_do_pitaco.base_models import BaseMarket


@dataclass
class ResultadoFinalMarket(BaseMarket):
    """Estrutura específica do mercado Resultado."""
    time_casa: str
    time_fora: str
    odd_time_casa: float
    odd_time_fora: float
    odd_empate: float
    is_pagamento_antecipado: bool
