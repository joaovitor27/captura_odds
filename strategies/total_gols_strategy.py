from typing import List
import pandas as pd
from selenium.webdriver.remote.webelement import WebElement

from database.repositories.total_gols_repository import TotalGolsRepository
from models.rei_do_pitaco.base_models import Match
from models.rei_do_pitaco.total_gols import TotalGolsMarket
from parsers.total_gols_parser import TotalGolsParser
from strategies.strategies import MarketStrategy

class TotalGolsStrategy(MarketStrategy):
    def __init__(self, repository: TotalGolsRepository) -> None:
        self.repository: TotalGolsRepository = repository
        self.accumulated_data: List[TotalGolsMarket] = []

    def can_handle(self, market_title: str) -> bool:
        return "Total De Gols" in market_title

    def parse_and_accumulate(self, element: WebElement, comp_name: str, match: Match) -> None:
        market_data_list = TotalGolsParser.parse(element, comp_name, match)
        if market_data_list:
            self.accumulated_data.extend(market_data_list)
            alvo = market_data_list[0].time_alvo
            print(f"⚽ [Total Gols - {alvo}] CAPTURADO: {len(market_data_list)} linhas encontradas para {match.home_team} x {match.away_team}")

    def save_to_db(self) -> None:
        if self.accumulated_data:
            print(f"💾 Salvando {len(self.accumulated_data)} odds de 'Total de Gols'...")
            self.repository.save_all(self.accumulated_data)
            self.accumulated_data.clear()

    def export_to_excel(self, writer: pd.ExcelWriter) -> None:
        query = "SELECT * FROM total_gols"

        with self.repository.db.get_connection() as conn:
            df = pd.read_sql_query(query, conn)

        if not df.empty:
            # Dropamos a coluna id gerada pelo BaseRepository
            if 'id' in df.columns:
                df = df.drop(columns=['id'])

            # Renomeando as colunas exatamente como na sua imagem de referência
            df = df.rename(columns={
                'data': 'Data',
                'hora': 'Hora',
                'competicao': 'Competição',
                'partida': 'Jogo',
                'time_alvo': 'Time',
                'mais_de': 'Mais de',
                'odd_mais_de': 'OLDs mais de',
                'menos_de': 'Menos de',
                'odd_menos_de': 'OLDs menos de'
            })

            colunas_ordenadas = ['Data', 'Hora','Competição', 'Jogo', 'Time', 'Mais de', 'OLDs mais de', 'Menos de', 'OLDs menos de']
            df = df[colunas_ordenadas]

            df.to_excel(writer, sheet_name="Total de Gols", index=False)
            print("📊 Aba 'Total de Gols' populada no Excel com sucesso.")