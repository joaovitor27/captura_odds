from typing import List
import pandas as pd

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

    def export_to_excel(self, writer: pd.ExcelWriter) -> None:
        """Consulta o SQLite e salva na aba do Excel correspondente."""
        query = "SELECT * FROM resultado_final"

        # Pega a conexão direto do gerenciador do repositório
        with self.repository.db.get_connection() as conn:
            df = pd.read_sql_query(query, conn)

        if not df.empty:
            # Escreve os dados em uma aba chamada "Resultado Final"
            df.to_excel(writer, sheet_name="Resultado Final", index=False)
            print("📊 Aba 'Resultado Final' populada no Excel com sucesso.")
