from dataclasses import dataclass
from models.rei_do_pitaco.base_models import BaseMarket

@dataclass
class FinalizacoesGolMarket(BaseMarket):
    """Estrutura específica do mercado Finalizações no Gol."""
    time_alvo: str
    mais_de: float
    odd_mais_de: float
    menos_de: float
    odd_menos_de: float
