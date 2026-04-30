from typing import List
import pandas as pd
from selenium.webdriver.remote.webelement import WebElement

from database.repositories.total_escanteios_repository import TotalEscanteiosRepository
from models.rei_do_pitaco.base_models import Match
from models.rei_do_pitaco.total_escanteios import TotalEscanteiosMarket
from parsers.total_escanteios_parser import TotalEscanteiosParser
from strategies.strategies import MarketStrategy

class TotalEscanteiosStrategy(MarketStrategy):
    def __init__(self, repository: TotalEscanteiosRepository) -> None:
        self.repository: TotalEscanteiosRepository = repository
        self.accumulated_data: List[TotalEscanteiosMarket] = []

    def can_handle(self, market_title: str) -> bool:
        return "Total de Escanteios" in market_title

    def parse_and_accumulate(self, element: WebElement, comp_name: str, match: Match) -> None:
        market_data_list = TotalEscanteiosParser.parse(element, comp_name, match)
        if market_data_list:
            self.accumulated_data.extend(market_data_list)
            alvo = market_data_list[0].time_alvo
            print(f"🚩 [Total Escanteios - {alvo}] CAPTURADO: {len(market_data_list)} linhas encontradas para {match.home_team} x {match.away_team}")

    def save_to_db(self) -> None:
        if self.accumulated_data:
            print(f"💾 Salvando {len(self.accumulated_data)} odds de 'Total de Escanteios'...")
            self.repository.save_all(self.accumulated_data)
            self.accumulated_data.clear()

    def export_to_excel(self, writer: pd.ExcelWriter) -> None:
        query = "SELECT * FROM total_escanteios"

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
                'time_alvo': 'Time',
                'mais_de': 'Mais de',
                'odd_mais_de': 'Odds mais de',
                'menos_de': 'Menos de',
                'odd_menos_de': 'Odds menos de'
            })

            colunas_ordenadas = ['Data', 'Hora', 'Competição', 'Jogo', 'Time', 'Mais de', 'Odds mais de', 'Menos de', 'Odds menos de']
            df = df[colunas_ordenadas]

            df.to_excel(writer, sheet_name="Total de Escanteios", index=False)
            print("📊 Aba 'Total de Escanteios' populada no Excel com sucesso.")
