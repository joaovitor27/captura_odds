from typing import Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from models.rei_do_pitaco.base_models import Match
from models.rei_do_pitaco.resultado_final import ResultadoFinalMarket


class ResultadoFinalParser:
    """Parser especialista em extrair os dados do card de Resultado Final."""

    @staticmethod
    def parse(element: WebElement, comp_name: str, match: Match) -> Optional[ResultadoFinalMarket]:
        try:
            # 1. Valida o título do mercado
            title_el = element.find_element(By.XPATH, ".//button[@data-testid='event-market-base-card-toggle']//span")
            market_title: str = str(title_el.get_attribute("textContent")).strip()

            if "Resultado Final" not in market_title:
                return None

            is_pagamento_antecipado: bool = "Pagamento Antecipado" in market_title

            # 2. Separa a Data e a Hora do objeto Match (Ex: "25/04, 18:30")
            data_hora_parts = match.datetime.split(", ")
            data_part = data_hora_parts[0].strip() if len(data_hora_parts) > 0 else match.datetime
            hora_part = data_hora_parts[1].strip() if len(data_hora_parts) > 1 else ""

            # 3. Extrai os botões de Odds (O HTML mostra sempre 3 botões em ordem: Casa, Empate, Fora)
            # Pegamos os parágrafos com o valor numérico que possui o 'x' no final (ex: "2.30x")
            odds_elements = element.find_elements(By.XPATH, ".//p[contains(text(), 'x')]")

            if len(odds_elements) < 3:
                return None

            # Limpa o "x" e converte para float
            odd_casa = float(str(odds_elements[0].get_attribute("textContent")).replace("x", "").strip())
            odd_empate = float(str(odds_elements[1].get_attribute("textContent")).replace("x", "").strip())
            odd_fora = float(str(odds_elements[2].get_attribute("textContent")).replace("x", "").strip())

            return ResultadoFinalMarket(
                competicao=comp_name,
                partida=f"{match.home_team} x {match.away_team}",
                data=data_part,
                hora=hora_part,
                time_casa=match.home_team,
                time_fora=match.away_team,
                odd_time_casa=odd_casa,
                odd_time_fora=odd_fora,
                odd_empate=odd_empate,
                is_pagamento_antecipado=is_pagamento_antecipado
            )

        except Exception as e:
            print(f"Erro ao fazer parse do mercado Resultado Final para o jogo {match.home_team}: {e}")
            return None