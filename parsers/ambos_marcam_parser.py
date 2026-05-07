from typing import Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from models.rei_do_pitaco.base_models import Match
from models.rei_do_pitaco.ambos_marcam import AmbosMarcamMarket

class AmbosMarcamParser:
    """Parser especialista em extrair os dados do card de Ambos Marcam."""

    @staticmethod
    def parse(element: WebElement, comp_name: str, match: Match) -> Optional[AmbosMarcamMarket]:
        try:
            # 1. Valida o título do mercado
            title_el = element.find_element(By.XPATH, ".//button[@data-testid='event-market-base-card-toggle']//span")
            market_title: str = str(title_el.get_attribute("textContent")).strip()

            if "Para Ambos os Times Marcarem" not in market_title and "Ambos Marcam" not in market_title:
                return None

            # 2. Separa a Data e a Hora do objeto Match
            data_hora_parts = match.datetime.split(", ")
            data_part = data_hora_parts[0].strip() if len(data_hora_parts) > 0 else match.datetime
            hora_part = data_hora_parts[1].strip() if len(data_hora_parts) > 1 else ""

            # 3. Extrai os botões
            buttons = element.find_elements(By.XPATH, ".//button[.//p]")
            if len(buttons) < 2:
                return None
            
            def extract_data(btn: WebElement) -> tuple[str, float]:
                ps = btn.find_elements(By.TAG_NAME, "p")
                if len(ps) >= 2:
                    nome = str(ps[0].get_attribute("textContent")).strip()
                    odd_str = str(ps[1].get_attribute("textContent")).replace("x", "").strip()
                    try:
                        odd = float(odd_str)
                    except ValueError:
                        odd = 0.0
                    return nome, odd
                return "", 0.0

            nome_1, odd_1 = extract_data(buttons[0])
            nome_2, odd_2 = extract_data(buttons[1])
            
            odd_sim = 0.0
            odd_nao = 0.0
            
            if nome_1.lower() == "sim":
                odd_sim = odd_1
            elif nome_1.lower() == "não" or nome_1.lower() == "nao":
                odd_nao = odd_1
                
            if nome_2.lower() == "sim":
                odd_sim = odd_2
            elif nome_2.lower() == "não" or nome_2.lower() == "nao":
                odd_nao = odd_2

            return AmbosMarcamMarket(
                competicao=comp_name,
                partida=f"{match.home_team} x {match.away_team}",
                data=data_part,
                hora=hora_part,
                odd_sim=odd_sim,
                odd_nao=odd_nao,
            )

        except Exception as e:
            print(f"Erro ao fazer parse do mercado Ambos Marcam para o jogo {match.home_team}: {e}")
            return None
