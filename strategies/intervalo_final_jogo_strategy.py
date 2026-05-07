from typing import List
import pandas as pd
from selenium.webdriver.remote.webelement import WebElement

from database.repositories.intervalo_final_jogo_repository import IntervaloFinalJogoRepository
from models.rei_do_pitaco.base_models import Match
from models.rei_do_pitaco.intervalo_final_jogo import IntervaloFinalJogoMarket
from parsers.intervalo_final_jogo_parser import IntervaloFinalJogoParser
from strategies.strategies import MarketStrategy

class IntervaloFinalJogoStrategy(MarketStrategy):
    def __init__(self, repository: IntervaloFinalJogoRepository) -> None:
        self.repository: IntervaloFinalJogoRepository = repository
        self.accumulated_data: List[IntervaloFinalJogoMarket] = []

    def can_handle(self, market_title: str) -> bool:
        return "Intervalo/Final do Jogo" in market_title

    def parse_and_accumulate(self, element: WebElement, comp_name: str, match: Match) -> None:
        market_data = IntervaloFinalJogoParser.parse(element, comp_name, match)
        if market_data:
            self.accumulated_data.append(market_data)
            print(f"✅ [Intervalo/Final do Jogo] CAPTURADO: {match.home_team} x {match.away_team}")

    def save_to_db(self) -> None:
        if self.accumulated_data:
            print(f"💾 Salvando {len(self.accumulated_data)} odds de 'Intervalo/Final do Jogo'...")
            self.repository.save_all(self.accumulated_data)
            self.accumulated_data.clear()

    def export_to_excel(self, writer: pd.ExcelWriter) -> None:
        query = "SELECT * FROM intervalo_final_jogo"

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
                'odd_opcao_3': 'Odd 3',
                'opcao_4': 'Opção 4',
                'odd_opcao_4': 'Odd 4',
                'opcao_5': 'Opção 5',
                'odd_opcao_5': 'Odd 5',
                'opcao_6': 'Opção 6',
                'odd_opcao_6': 'Odd 6',
                'opcao_7': 'Opção 7',
                'odd_opcao_7': 'Odd 7',
                'opcao_8': 'Opção 8',
                'odd_opcao_8': 'Odd 8',
                'opcao_9': 'Opção 9',
                'odd_opcao_9': 'Odd 9',
            })

            colunas_ordenadas = [
                'Data', 'Hora', 'Competição', 'Jogo', 
                'Opção 1', 'Odd 1', 'Opção 2', 'Odd 2', 'Opção 3', 'Odd 3',
                'Opção 4', 'Odd 4', 'Opção 5', 'Odd 5', 'Opção 6', 'Odd 6',
                'Opção 7', 'Odd 7', 'Opção 8', 'Odd 8', 'Opção 9', 'Odd 9'
            ]
            df = df[colunas_ordenadas]

            df.to_excel(writer, sheet_name="Intervalo Final", index=False)
            print("📊 Aba 'Intervalo Final' populada no Excel com sucesso.")
