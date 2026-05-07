from typing import List
import pandas as pd
from selenium.webdriver.remote.webelement import WebElement

from database.repositories.finalizacoes_gol_repository import FinalizacoesGolRepository
from models.rei_do_pitaco.base_models import Match
from models.rei_do_pitaco.finalizacoes_gol import FinalizacoesGolMarket
from parsers.finalizacoes_gol_parser import FinalizacoesGolParser
from strategies.strategies import MarketStrategy

class FinalizacoesGolStrategy(MarketStrategy):
    def __init__(self, repository: FinalizacoesGolRepository) -> None:
        self.repository: FinalizacoesGolRepository = repository
        self.accumulated_data: List[FinalizacoesGolMarket] = []

    def can_handle(self, market_title: str) -> bool:
        return "Finalizações no Gol" in market_title

    def parse_and_accumulate(self, element: WebElement, comp_name: str, match: Match) -> None:
        market_data_list = FinalizacoesGolParser.parse(element, comp_name, match)
        if market_data_list:
            self.accumulated_data.extend(market_data_list)
            alvo = market_data_list[0].time_alvo
            print(f"🎯 [Finalizações no Gol - {alvo}] CAPTURADO: {len(market_data_list)} linhas encontradas para {match.home_team} x {match.away_team}")

    def save_to_db(self) -> None:
        if self.accumulated_data:
            print(f"💾 Salvando {len(self.accumulated_data)} odds de 'Finalizações no Gol'...")
            self.repository.save_all(self.accumulated_data)
            self.accumulated_data.clear()

    def export_to_excel(self, writer: pd.ExcelWriter) -> None:
        query = "SELECT * FROM finalizacoes_gol"

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

            df.to_excel(writer, sheet_name="Finalizações no Gol", index=False)
            print("📊 Aba 'Finalizações no Gol' populada no Excel com sucesso.")
