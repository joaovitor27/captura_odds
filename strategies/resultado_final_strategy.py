from typing import List

from selenium.webdriver.remote.webelement import WebElement

from models.rei_do_pitado_models import ResultadoFinalMarket, Match
from database.repositories.resultado_final_repository import ResultadoFinalRepository
from scrapers.market_parsers import ResultadoFinalParser
from strategies.strategies import MarketStrategy


class ResultadoFinalStrategy(MarketStrategy):
    def __init__(self, repository: ResultadoFinalRepository) -> None:
        self.repository: ResultadoFinalRepository = repository
        self.accumulated_data: List[ResultadoFinalMarket] = []

    def can_handle(self, market_title: str) -> bool:
        return "Resultado Final" in market_title

    def parse_and_accumulate(self, element: WebElement, comp_name: str, match: Match) -> None:
        market_data = ResultadoFinalParser.parse(element, comp_name, match)
        if market_data:
            self.accumulated_data.append(market_data)
            print(
                f"✅[Resultado Final] ODD CAPTURADA: {match.home_team} ({market_data.odd_time_casa}) | Empate ({market_data.odd_empate}) | {match.away_team} ({market_data.odd_time_fora})")

    def save_to_db(self) -> None:
        if self.accumulated_data:
            print(f"💾 Salvando {len(self.accumulated_data)} odds de 'Resultado Final'...")
            self.repository.save_all(self.accumulated_data)
            self.accumulated_data.clear()
