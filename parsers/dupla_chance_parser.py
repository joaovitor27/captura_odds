from typing import Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from models.rei_do_pitaco.base_models import Match
from models.rei_do_pitaco.dupla_chance import DuplaChanceMarket

class DuplaChanceParser:
    """Parser especialista em extrair os dados do card de Dupla Chance."""

    @staticmethod
    def parse(element: WebElement, comp_name: str, match: Match) -> Optional[DuplaChanceMarket]:
        try:
            # 1. Valida o título do mercado
            title_el = element.find_element(By.XPATH, ".//button[@data-testid='event-market-base-card-toggle']//span")
            market_title: str = str(title_el.get_attribute("textContent")).strip()

            if "Dupla chance" not in market_title:
                return None

            # 2. Separa a Data e a Hora do objeto Match
            data_hora_parts = match.datetime.split(", ")
            data_part = data_hora_parts[0].strip() if len(data_hora_parts) > 0 else match.datetime
            hora_part = data_hora_parts[1].strip() if len(data_hora_parts) > 1 else ""

            # 3. Extrai os botões
            # No HTML fornecido os botões contêm <p> com as opções e odds
            buttons = element.find_elements(By.XPATH, ".//button[.//p]")
            if len(buttons) < 3:
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

            opcao_1, odd_1 = extract_data(buttons[0])
            opcao_2, odd_2 = extract_data(buttons[1])
            opcao_3, odd_3 = extract_data(buttons[2])

            return DuplaChanceMarket(
                competicao=comp_name,
                partida=f"{match.home_team} x {match.away_team}",
                data=data_part,
                hora=hora_part,
                opcao_1=opcao_1,
                odd_opcao_1=odd_1,
                opcao_2=opcao_2,
                odd_opcao_2=odd_2,
                opcao_3=opcao_3,
                odd_opcao_3=odd_3,
            )

        except Exception as e:
            print(f"Erro ao fazer parse do mercado Dupla Chance para o jogo {match.home_team}: {e}")
            return None
