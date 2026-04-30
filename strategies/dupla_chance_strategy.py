from typing import List
import pandas as pd
from selenium.webdriver.remote.webelement import WebElement

from database.repositories.dupla_chance_repository import DuplaChanceRepository
from models.rei_do_pitaco.base_models import Match
from models.rei_do_pitaco.dupla_chance import DuplaChanceMarket
from parsers.dupla_chance_parser import DuplaChanceParser
from strategies.strategies import MarketStrategy

class DuplaChanceStrategy(MarketStrategy):
    def __init__(self, repository: DuplaChanceRepository) -> None:
        self.repository: DuplaChanceRepository = repository
        self.accumulated_data: List[DuplaChanceMarket] = []

    def can_handle(self, market_title: str) -> bool:
        return "Dupla chance" in market_title

    def parse_and_accumulate(self, element: WebElement, comp_name: str, match: Match) -> None:
        market_data = DuplaChanceParser.parse(element, comp_name, match)
        if market_data:
            self.accumulated_data.append(market_data)
            print(f"✅ [Dupla Chance] CAPTURADO: {match.home_team} x {match.away_team}")

    def save_to_db(self) -> None:
        if self.accumulated_data:
            print(f"💾 Salvando {len(self.accumulated_data)} odds de 'Dupla Chance'...")
            self.repository.save_all(self.accumulated_data)
            self.accumulated_data.clear()

    def export_to_excel(self, writer: pd.ExcelWriter) -> None:
        query = "SELECT * FROM dupla_chance"

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
                'opcao_1': 'Opção 1',
                'odd_opcao_1': 'Odd 1',
                'opcao_2': 'Opção 2',
                'odd_opcao_2': 'Odd 2',
                'opcao_3': 'Opção 3',
                'odd_opcao_3': 'Odd 3'
            })

            colunas_ordenadas = ['Data', 'Hora', 'Competição', 'Jogo', 'Opção 1', 'Odd 1', 'Opção 2', 'Odd 2', 'Opção 3', 'Odd 3']
            df = df[colunas_ordenadas]

            df.to_excel(writer, sheet_name="Dupla Chance", index=False)
            print("📊 Aba 'Dupla Chance' populada no Excel com sucesso.")
