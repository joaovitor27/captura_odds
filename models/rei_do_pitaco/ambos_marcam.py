from dataclasses import dataclass
from models.rei_do_pitaco.base_models import BaseMarket

@dataclass
class AmbosMarcamMarket(BaseMarket):
    """Estrutura específica do mercado Ambos Marcam."""
    odd_sim: float
    odd_nao: float
