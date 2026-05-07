from typing import List
import pandas as pd
from selenium.webdriver.remote.webelement import WebElement

from database.repositories.primeiro_tempo_resultado_repository import PrimeiroTempoResultadoRepository
from models.rei_do_pitaco.base_models import Match
from models.rei_do_pitaco.primeiro_tempo_resultado import PrimeiroTempoResultadoMarket
from parsers.primeiro_tempo_resultado_parser import PrimeiroTempoResultadoParser
from strategies.strategies import MarketStrategy

class PrimeiroTempoResultadoStrategy(MarketStrategy):
    def __init__(self, repository: PrimeiroTempoResultadoRepository) -> None:
        self.repository: PrimeiroTempoResultadoRepository = repository
        self.accumulated_data: List[PrimeiroTempoResultadoMarket] = []

    def can_handle(self, market_title: str) -> bool:
        return "1º Tempo - Resultado" in market_title

    def parse_and_accumulate(self, element: WebElement, comp_name: str, match: Match) -> None:
        market_data = PrimeiroTempoResultadoParser.parse(element, comp_name, match)
        if market_data:
            self.accumulated_data.append(market_data)
            print(f"✅ [1º Tempo - Resultado] CAPTURADO: {match.home_team} x {match.away_team}")

    def save_to_db(self) -> None:
        if self.accumulated_data:
            print(f"💾 Salvando {len(self.accumulated_data)} odds de '1º Tempo - Resultado'...")
            self.repository.save_all(self.accumulated_data)
            self.accumulated_data.clear()

    def export_to_excel(self, writer: pd.ExcelWriter) -> None:
        query = "SELECT * FROM primeiro_tempo_resultado"

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
                'time_casa': 'Time Casa',
                'odd_time_casa': 'Odd Casa',
                'odd_empate': 'Odd Empate',
                'time_fora': 'Time Fora',
                'odd_time_fora': 'Odd Fora',
                'is_pagamento_antecipado': 'Pagamento Antecipado'
            })

            colunas_ordenadas = ['Data', 'Hora', 'Competição', 'Jogo', 'Time Casa', 'Odd Casa', 'Odd Empate', 'Odd Fora', 'Time Fora', 'Pagamento Antecipado']
            df = df[colunas_ordenadas]

            df.to_excel(writer, sheet_name="1º Tempo - Resultado", index=False)
            print("📊 Aba '1º Tempo - Resultado' populada no Excel com sucesso.")
