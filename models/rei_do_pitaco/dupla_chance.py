from dataclasses import dataclass
from models.rei_do_pitaco.base_models import BaseMarket

@dataclass
class DuplaChanceMarket(BaseMarket):
    """Estrutura específica do mercado de Dupla Chance."""
    opcao_1: str
    odd_opcao_1: float
    opcao_2: str
    odd_opcao_2: float
    opcao_3: str
    odd_opcao_3: float
