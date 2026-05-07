from typing import List
import pandas as pd
from selenium.webdriver.remote.webelement import WebElement

from database.repositories.ambos_marcam_repository import AmbosMarcamRepository
from models.rei_do_pitaco.base_models import Match
from models.rei_do_pitaco.ambos_marcam import AmbosMarcamMarket
from parsers.ambos_marcam_parser import AmbosMarcamParser
from strategies.strategies import MarketStrategy

class AmbosMarcamStrategy(MarketStrategy):
    def __init__(self, repository: AmbosMarcamRepository) -> None:
        self.repository: AmbosMarcamRepository = repository
        self.accumulated_data: List[AmbosMarcamMarket] = []

    def can_handle(self, market_title: str) -> bool:
        return "Para Ambos os Times Marcarem" in market_title or "Ambos Marcam" in market_title

    def parse_and_accumulate(self, element: WebElement, comp_name: str, match: Match) -> None:
        market_data = AmbosMarcamParser.parse(element, comp_name, match)
        if market_data:
            self.accumulated_data.append(market_data)
            print(f"✅ [Ambos Marcam] CAPTURADO: {match.home_team} x {match.away_team}")

    def save_to_db(self) -> None:
        if self.accumulated_data:
            print(f"💾 Salvando {len(self.accumulated_data)} odds de 'Ambos Marcam'...")
            self.repository.save_all(self.accumulated_data)
            self.accumulated_data.clear()

    def export_to_excel(self, writer: pd.ExcelWriter) -> None:
        query = "SELECT * FROM ambos_marcam"

        with self.repository.db.get_connection() as conn:
            df = pd.read_sql_query(query, conn)

        if not df.empty:
            if 'id' in df.columns:
                df = df.drop(columns=['id'])

            df = df.rename(columns={
                'data': 'Data',
                'hora': 'Hora',
                'competicao': 'Competição',
                'partida': 'Jogo',
                'odd_sim': 'ODD Sim',
                'odd_nao': 'ODD Não',
            })

            colunas_ordenadas = ['Data', 'Hora', 'Competição', 'Jogo', 'ODD Sim', 'ODD Não']
            df = df[colunas_ordenadas]

            df.to_excel(writer, sheet_name="Ambos Marcam", index=False)
            print("📊 Aba 'Ambos Marcam' populada no Excel com sucesso.")
