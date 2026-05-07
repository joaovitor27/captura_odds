from typing import List
import pandas as pd
from selenium.webdriver.remote.webelement import WebElement

from database.repositories.defesas_goleiro_repository import DefesasGoleiroRepository
from models.rei_do_pitaco.base_models import Match
from models.rei_do_pitaco.defesas_goleiro import DefesasGoleiroMarket
from parsers.defesas_goleiro_parser import DefesasGoleiroParser
from strategies.strategies import MarketStrategy

class DefesasGoleiroStrategy(MarketStrategy):
    def __init__(self, repository: DefesasGoleiroRepository) -> None:
        self.repository: DefesasGoleiroRepository = repository
        self.accumulated_data: List[DefesasGoleiroMarket] = []

    def can_handle(self, market_title: str) -> bool:
        return "Defesas de Goleiro" in market_title

    def parse_and_accumulate(self, element: WebElement, comp_name: str, match: Match) -> None:
        market_data_list = DefesasGoleiroParser.parse(element, comp_name, match)
        if market_data_list:
            self.accumulated_data.extend(market_data_list)
            alvo = market_data_list[0].time_alvo
            print(f"🧤 [Defesas de Goleiro - {alvo}] CAPTURADO: {len(market_data_list)} linhas encontradas para {match.home_team} x {match.away_team}")

    def save_to_db(self) -> None:
        if self.accumulated_data:
            print(f"💾 Salvando {len(self.accumulated_data)} odds de 'Defesas de Goleiro'...")
            self.repository.save_all(self.accumulated_data)
            self.accumulated_data.clear()

    def export_to_excel(self, writer: pd.ExcelWriter) -> None:
        query = "SELECT * FROM defesas_goleiro"

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
                'time_alvo': 'Time Alvo',
                'mais_de': 'Mais De',
                'odd_mais_de': 'Odd Mais De',
                'menos_de': 'Menos De',
                'odd_menos_de': 'Odd Menos De'
            })

            colunas_ordenadas = ['Data', 'Hora', 'Competição', 'Jogo', 'Time Alvo', 'Mais De', 'Odd Mais De', 'Menos De', 'Odd Menos De']
            df = df[colunas_ordenadas]

            df.to_excel(writer, sheet_name="Defesas de Goleiro", index=False)
            print("📊 Aba 'Defesas de Goleiro' populada no Excel com sucesso.")
