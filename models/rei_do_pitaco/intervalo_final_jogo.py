from dataclasses import dataclass
from models.rei_do_pitaco.base_models import BaseMarket

@dataclass
class IntervaloFinalJogoMarket(BaseMarket):
    """Estrutura específica do mercado Intervalo/Final do Jogo."""
    opcao_1: str
    odd_opcao_1: float
    opcao_2: str
    odd_opcao_2: float
    opcao_3: str
    odd_opcao_3: float
    opcao_4: str
    odd_opcao_4: float
    opcao_5: str
    odd_opcao_5: float
    opcao_6: str
    odd_opcao_6: float
    opcao_7: str
    odd_opcao_7: float
    opcao_8: str
    odd_opcao_8: float
    opcao_9: str
    odd_opcao_9: float
