import time
from typing import Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from models.rei_do_pitaco.base_models import Match
from models.rei_do_pitaco.intervalo_final_jogo import IntervaloFinalJogoMarket

class IntervaloFinalJogoParser:
    """Parser especialista em extrair os dados do card de Intervalo/Final do Jogo."""

    @staticmethod
    def parse(element: WebElement, comp_name: str, match: Match) -> Optional[IntervaloFinalJogoMarket]:
        try:
            # 1. Valida o título do mercado
            title_el = element.find_element(By.XPATH, ".//button[@data-testid='event-market-base-card-toggle']//span")
            market_title: str = str(title_el.get_attribute("textContent")).strip()

            if "Intervalo/Final do Jogo" not in market_title:
                return None

            driver = element.parent  # Pega a instância do WebDriver a partir do elemento

            # 2. Verifica e clica no botão "Mostrar mais"
            try:
                btn_mostrar_mais = element.find_element(By.XPATH, ".//button[contains(., 'Mostrar mais')]")
                driver.execute_script("arguments[0].click();", btn_mostrar_mais)
                time.sleep(0.5)

                xpath_re_fetch = f"//div[@data-testid='event-market-base-card' and .//span[contains(text(), '{market_title}')]]"
                element = driver.find_element(By.XPATH, xpath_re_fetch)
            except Exception:
                pass

            # 3. Separa a Data e a Hora do objeto Match
            data_hora_parts = match.datetime.split(", ")
            data_part = data_hora_parts[0].strip() if len(data_hora_parts) > 0 else match.datetime
            hora_part = data_hora_parts[1].strip() if len(data_hora_parts) > 1 else ""

            # 4. Extrai os botões
            buttons = element.find_elements(By.XPATH, ".//button[.//p]")
            
            # Filtramos botões que possam ser "Mostrar mais/menos" e garantimos os válidos
            valid_buttons = []
            for btn in buttons:
                ps = btn.find_elements(By.TAG_NAME, "p")
                if len(ps) >= 2 and "/" in ps[0].get_attribute("textContent"):
                    valid_buttons.append(btn)

            if len(valid_buttons) < 9:
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

            opcoes_odds = [extract_data(btn) for btn in valid_buttons[:9]]

            return IntervaloFinalJogoMarket(
                competicao=comp_name,
                partida=f"{match.home_team} x {match.away_team}",
                data=data_part,
                hora=hora_part,
                opcao_1=opcoes_odds[0][0], odd_opcao_1=opcoes_odds[0][1],
                opcao_2=opcoes_odds[1][0], odd_opcao_2=opcoes_odds[1][1],
                opcao_3=opcoes_odds[2][0], odd_opcao_3=opcoes_odds[2][1],
                opcao_4=opcoes_odds[3][0], odd_opcao_4=opcoes_odds[3][1],
                opcao_5=opcoes_odds[4][0], odd_opcao_5=opcoes_odds[4][1],
                opcao_6=opcoes_odds[5][0], odd_opcao_6=opcoes_odds[5][1],
                opcao_7=opcoes_odds[6][0], odd_opcao_7=opcoes_odds[6][1],
                opcao_8=opcoes_odds[7][0], odd_opcao_8=opcoes_odds[7][1],
                opcao_9=opcoes_odds[8][0], odd_opcao_9=opcoes_odds[8][1],
            )

        except Exception as e:
            print(f"Erro ao fazer parse do mercado Intervalo/Final do Jogo para o jogo {match.home_team}: {e}")
            return None
