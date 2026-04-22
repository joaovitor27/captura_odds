import pandas as pd
from abc import ABC, abstractmethod
from selenium.webdriver.remote.webelement import WebElement

from models.rei_do_pitaco.base_models import Match


class MarketStrategy(ABC):
    """Contrato base para todos os extratores de mercados."""

    @abstractmethod
    def can_handle(self, market_title: str) -> bool:
        """Define se esta estratégia sabe processar este mercado."""
        pass

    @abstractmethod
    def parse_and_accumulate(self, element: WebElement, comp_name: str, match: Match) -> None:
        """Extrai os dados do HTML e guarda na memória da estratégia."""
        pass

    @abstractmethod
    def save_to_db(self) -> None:
        """Envia os dados acumulados para o respectivo repositório."""
        pass

    @abstractmethod
    def export_to_excel(self, writer: pd.ExcelWriter) -> None:
        """Exporta os dados do banco para uma aba (sheet) no Excel."""
        pass
