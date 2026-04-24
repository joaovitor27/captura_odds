from dataclasses import dataclass
from models.rei_do_pitaco.base_models import BaseMarket

@dataclass
class TotalGolsMarket(BaseMarket):
    """Estrutura específica do mercado Total de Gols (Over/Under)."""
    time_alvo: str  # Pode ser 'partida', ou o nome do time específico
    mais_de: float
    odd_mais_de: float
    menos_de: float
    odd_menos_de: float