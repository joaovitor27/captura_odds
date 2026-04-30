import time
from typing import List, Tuple
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from models.rei_do_pitaco.base_models import Match
from models.rei_do_pitaco.total_escanteios import TotalEscanteiosMarket
from utils.logger import console


class TotalEscanteiosParser:
    """Parser especialista em extrair os dados do card de Total de Escanteios (Over/Under)."""

    @staticmethod
    def parse(element: WebElement, comp_name: str, match: Match) -> List[TotalEscanteiosMarket]:
        resultados: List[TotalEscanteiosMarket] = []
        try:
            # 1. Valida o título do mercado e descobre o Alvo
            title_el = element.find_element(By.XPATH, ".//button[@data-testid='event-market-base-card-toggle']//span")
            market_title: str = str(title_el.get_attribute("textContent")).strip()

            if "Total de Escanteios" not in market_title:
                return resultados

            time_alvo: str = "partida"
            if "-" in market_title:
                time_alvo = market_title.split("-")[0].strip()

            driver = element.parent  # Pega a instância do WebDriver a partir do elemento

            # 2. Verifica e clica no botão "Mostrar mais"
            try:
                btn_mostrar_mais = element.find_element(By.XPATH, ".//button[.//p[text()='Mostrar mais']]")
                driver.execute_script("arguments[0].click();", btn_mostrar_mais)
                time.sleep(0.5)  # Aguarda a animação do React

                # 🛑 CORREÇÃO CRÍTICA DO REACT VIRTUOSO:
                # Ao expandir, o card é recriado na DOM. Precisamos re-buscar o elemento pelo título!
                xpath_re_fetch = f"//div[@data-testid='event-market-base-card' and .//span[contains(text(), '{market_title}')]]"
                element = driver.find_element(By.XPATH, xpath_re_fetch)
            except Exception:
                pass  # O botão não existe, usa o element original mesmo

            # 3. Extrai dados base
            data_hora_parts = match.datetime.split(", ")
            data_part: str = data_hora_parts[0].strip() if len(data_hora_parts) > 0 else match.datetime
            hora_part: str = data_hora_parts[1].strip() if len(data_hora_parts) > 1 else ""

            # 4. Localiza as colunas (A classe flex-1 engloba a coluna inteira)
            colunas = element.find_elements(By.XPATH, ".//div[contains(@class, 'flex-1')]")
            if len(colunas) < 2:
                return resultados

            botoes_mais = colunas[0].find_elements(By.XPATH, ".//button")
            botoes_menos = colunas[1].find_elements(By.XPATH, ".//button")

            # 5. Itera montando os objetos
            for idx in range(max(len(botoes_mais), len(botoes_menos))):
                linha_mais, odd_m = TotalEscanteiosParser._extract_linha_odd(botoes_mais[idx]) if idx < len(botoes_mais) else (0.0, 0.0)
                linha_menos, odd_n = TotalEscanteiosParser._extract_linha_odd(botoes_menos[idx]) if idx < len(botoes_menos) else (0.0, 0.0)

                if odd_m == 0.0 and odd_n == 0.0:
                    continue

                resultados.append(TotalEscanteiosMarket(
                    data=data_part,
                    hora=hora_part,
                    partida=f"{match.home_team} x {match.away_team}",
                    competicao=comp_name,
                    time_alvo=time_alvo.lower(),
                    mais_de=linha_mais,
                    odd_mais_de=odd_m,
                    menos_de=linha_menos,
                    odd_menos_de=odd_n
                ))

            return resultados

        except Exception as e:
            # Se cair aqui (ex: StaleElement no meio da leitura das odds), o loop de cima
            # não vai marcar como lido, garantindo uma nova tentativa!
            raise e

    @staticmethod
    def _extract_linha_odd(btn: WebElement) -> Tuple[float, float]:
        try:
            if btn.get_attribute("disabled") == "true" or btn.get_attribute("disabled") == "":
                return 0.0, 0.0

            ps = btn.find_elements(By.TAG_NAME, "p")
            if len(ps) >= 2:
                linha = float(str(ps[0].get_attribute("textContent")).strip())
                odd = float(str(ps[1].get_attribute("textContent")).replace("x", "").strip())
                return linha, odd
        except Exception:
            pass

        return 0.0, 0.0
