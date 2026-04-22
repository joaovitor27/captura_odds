from chromium import CustomWebDriver
from driver import DriverUtils
from models.rei_do_pitado_models import Competition, Category, Match, ResultadoFinalMarket

import time
from typing import List, Set, Dict, Tuple
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from strategies.strategies import MarketStrategy
from utils.logger import console


class ReiDoPitacoMarketExplorer:
    """
    Classe responsável por acessar os detalhes de cada partida,
    navegar pelas abas e mapear todos os tipos de apostas únicos (Mercados).
    Lida nativamente com listas virtualizadas (React Virtuoso) e eventos sintéticos.
    """

    def __init__(self, driver: CustomWebDriver, strategies: List[MarketStrategy]) -> None:
        self.driver: CustomWebDriver = driver
        self.strategies: List[MarketStrategy] = strategies
        self.unique_markets: Set[str] = set()
        self.base_url: str = 'https://reidopitaco.bet.br/betting/sports/20000000169?tab=competitions'

    def discover_unique_markets(self, competitions: List[Competition]) -> Tuple[Set[str], List[ResultadoFinalMarket]]:
        """
        Itera sobre o mapeamento prévio de competições, acessando os detalhes de cada partida 
        para mapear e acumular todos os tipos de apostas (mercados) únicos.
        
        Args:
            competitions (List[Competition]): Lista de competições a serem exploradas.
            
        Returns:
            Tuple[Set[str], List[ResultadoFinalMarket]]: Tupla contendo os mercados únicos encontrados 
                                                        e a lista de odds registradas.
        """
        todas_odds_resultado_final: List[ResultadoFinalMarket] = []
        for comp in competitions:
            if not comp.matches:
                continue

            print(f"\n🔍 Explorando mercados da competição: {comp.name}")

            if comp.url:
                self.driver.get(comp.url)
                time.sleep(1.5)
            else:
                console.print(f"  [danger][Erro] URL não encontrada para {comp.name}. Pulando.[/danger]")
                continue

            for match in comp.matches:
                for attempt in range(1, 4):
                    try:
                        xpath_match_card: str = f"(//div[@aria-label='UIOneAgainstTwoPreEventLine' and contains(., '{match.home_team}')]//div[@role='button'])[1]"
                        match_el: WebElement = DriverUtils.wait_presence_by_xpath(self.driver, xpath_match_card,
                                                                                  timeout=10)

                        try:
                            match_el.click()
                        except:
                            self.driver.execute_script("arguments[0].click();", match_el)

                        xpath_tab_todos: str = "//button[@role='tab' and contains(., 'Todos')]"
                        DriverUtils.wait_presence_by_xpath(self.driver, xpath_tab_todos, timeout=10)

                        odds_da_partida = self._extract_markets_from_match_page(comp.name, match)
                        if odds_da_partida:
                            todas_odds_resultado_final.extend(odds_da_partida)

                        self.driver.back()
                        time.sleep(1.5)
                        break

                    except Exception as e:
                        console.print(
                            f"  [warning][Aviso] Falha de rota para {match.home_team} x {match.away_team} (Tentativa {attempt}). Erro: {type(e).__name__}[/warning]")
                        if attempt == 3:
                            console.print(f"  [danger][Erro] Abortando a exploração do jogo {match.home_team}.[/danger]")
                        else:
                            self.driver.get(comp.url)
                            time.sleep(2)

        return self.unique_markets, todas_odds_resultado_final

    def _extract_markets_from_match_page(self, comp_name: str, match: Match) -> list[ResultadoFinalMarket] | None:
        """
        Lida com a interface do jogo: Clica na aba 'Todos', rola o contêiner
        virtualizado e extrai nomes únicos em tempo real.
        """
        try:
            xpath_tab_todos: str = "//button[@role='tab' and contains(., 'Todos')]"
            tab_todos: WebElement = DriverUtils.wait_presence_by_xpath(self.driver, xpath_tab_todos, timeout=10)

            # Só clica se já não estiver ativo
            if "Mui-selected" not in str(tab_todos.get_attribute("class")):
                self.driver.execute_script("arguments[0].click();", tab_todos)
                time.sleep(1)
        except Exception:
            # console.print(f"  [warning]-> Aba 'Todos' ausente na página do jogo.[/warning]")
            return

        try:
            scroller_xpath: str = "//div[@data-virtuoso-scroller='true']"
            scroller_el: WebElement = DriverUtils.wait_presence_by_xpath(self.driver, scroller_xpath, timeout=5)
        except Exception:
            # console.print("  [warning]-> Contêiner virtualizado de apostas não encontrado.[/warning]")
            return

        scraped_resultado_final: List[ResultadoFinalMarket] = []

        while True:
            # Seleciona o card base completo (a div que engloba o mercado inteiro)
            market_cards_xpath: str = "//div[@data-testid='event-market-base-card']"
            visible_market_cards: List[WebElement] = self.driver.find_elements(By.XPATH, market_cards_xpath)

            for card_el in visible_market_cards:
                # Extraímos o título para não reprocessar cards que já analisamos neste jogo
                title_el = card_el.find_element(By.XPATH,
                                                ".//button[@data-testid='event-market-base-card-toggle']//span")
                market_title: str = str(title_el.get_attribute("textContent")).strip()

                if market_title:
                    if market_title not in self.unique_markets:
                        self.unique_markets.add(market_title)
                        console.print(f"  [success]↳ NOVO MERCADO ENCONTRADO NO SITE: {market_title}[/success]")

                    for strategy in self.strategies:
                        if strategy.can_handle(market_title):
                            strategy.parse_and_accumulate(card_el, comp_name, match)
                            break

                    # Futuramente: elif "Total De Gols" in market_title: ...

            self.driver.execute_script("arguments[0].scrollTop += arguments[0].clientHeight;", scroller_el)
            time.sleep(0.5)

            is_at_bottom: bool = bool(self.driver.execute_script(
                "return Math.ceil(arguments[0].scrollTop + arguments[0].clientHeight) >= arguments[0].scrollHeight;",
                scroller_el
            ))

            if is_at_bottom:
                break

        return scraped_resultado_final


class ReiDoPitacoScraper:
    """
    Classe responsável por extrair competições do site Rei do Pitaco.
    Garante a captura em memória de forma fluida sem interações desnecessárias na UI.
    """

    # Mapeamento estrito das ligas desejadas. O uso parcial dos nomes
    # previne falhas causadas por alteração de emojis no DOM.
    TARGET_CATEGORIES: List[str] = [
        "Brasil no topo!!",
        "Melhores do Mundo",
        "O Melhor da Europa",
        "O Melhor da América",
        "Rumo à Copa",
        "Argentina",
        "Chile",
        "Clubes Internacionais",
        "Colômbia",
        "Equador",
        "Paraguai",
        "Peru",
        "Uruguai",
        "Venezuela",
        "Brasil"
    ]

    def __init__(self, driver: CustomWebDriver) -> None:
        self.driver: CustomWebDriver = driver
        self.base_url: str = 'https://reidopitaco.bet.br/betting/sports/20000000169?tab=competitions'

    def refresh_matches_from_urls(self, competitions: List[Competition]) -> None:
        """
        Acessa as URLs diretas em cache para atualizar os jogos do dia rapidamente,
        sem precisar passar pela página principal.
        """
        # console.print("[info]🔄 Atualizando lista de jogos do dia usando URLs em cache...[/info]")
        for comp in competitions:
            if not comp.url:
                continue

            try:
                self.driver.get(comp.url)
                # O método abaixo já tem o DriverUtils.wait_presence_by_xpath integrado
                comp.matches = self._parse_matches_from_page()
            except Exception as e:
                console.print(f"  [danger][Erro] Falha ao atualizar jogos para {comp.name}: {e}[/danger]")

    def fetch_all_competitions(self) -> Dict[str, Category]:
        """Acessa a página principal e guarda em memória todas as competições configuradas."""
        self.driver.get(self.base_url)

        # Aguarda a estrutura principal de competições carregar na DOM
        DriverUtils.wait_presence_by_xpath(
            self.driver,
            "//div[contains(@class, 'MuiCollapse-root')]",
            timeout=10
        )

        scraped_data: Dict[str, Category] = {}

        for cat_name in self.TARGET_CATEGORIES:
            competitions: List[Competition] = self._extract_category_competitions(cat_name)
            if competitions:
                scraped_data[cat_name] = Category(name=cat_name, competitions=competitions)

        return scraped_data

    def _extract_category_competitions(self, category_name: str) -> List[Competition]:
        """
        Extrai as competições de uma categoria específica diretamente da DOM.
        Lê o textContent, ignorando as restrições visuais do MuiCollapse.
        
        Args:
            category_name (str): O nome da categoria alvo.
            
        Returns:
            List[Competition]: Uma lista de competições encontradas.
        """
        xpath: str = (
            f"//span[contains(text(), '{category_name}')]"
            f"/ancestor::div[following-sibling::div[contains(@class, 'MuiCollapse-root')]][1]"
            f"/following-sibling::div[contains(@class, 'MuiCollapse-root')]"
            f"//span[contains(@class, 'mui-ymly3k')]"
        )

        try:
            # Usamos find_elements diretamente pois a DOM já está carregada.
            elements: List[WebElement] = self.driver.find_elements(By.XPATH, xpath)
            competitions: List[Competition] = []

            for el in elements:
                # O uso de 'textContent' permite extrair o texto mesmo que o menu
                # esteja invisível (display:none), poupando tempo de cliques e waits.
                text: str = str(el.get_attribute("textContent")).strip()
                if text:
                    competitions.append(Competition(name=text))

            return competitions

        except Exception as e:
            console.print(f"[danger]Erro ao tentar extrair a categoria '{category_name}': {e}[/danger]")
            return []

    def scrape_all_unique_competitions(self) -> List[Competition]:
        categories_dict = self.fetch_all_competitions()

        unique_comp_names: Set[str] = set()
        for cat in categories_dict.values():
            for comp in cat.competitions:
                unique_comp_names.add(comp.name)

        console.print(f"[success]Total de competições ÚNICAS para mapear: {len(unique_comp_names)}[/success]")
        scraped_competitions: List[Competition] = []

        for comp_name in unique_comp_names:
            console.print(f"[dim]Mapeando jogos de: {comp_name}...[/dim]")
            # Desempacota a tupla
            matches, comp_url = self._navigate_and_extract_matches(comp_name, max_retries=3)

            scraped_competitions.append(Competition(name=comp_name, url=comp_url, matches=matches))

        return scraped_competitions

    def _navigate_and_extract_matches(self, comp_name: str, max_retries: int = 3) -> Tuple[List[Match], str]:
        for attempt in range(1, max_retries + 1):
            try:
                if "competitions" not in self.driver.current_url:
                    self.driver.get(self.base_url)
                    DriverUtils.wait_presence_by_xpath(self.driver, "//div[contains(@class, 'MuiCollapse-root')]",
                                                       timeout=15)

                xpath_comp = f"(//span[contains(@class, 'mui-ymly3k') and normalize-space(.)='{comp_name}'])[1]"
                comp_element = DriverUtils.wait_presence_by_xpath(self.driver, xpath_comp, timeout=10)

                self.driver.execute_script("arguments[0].click();", comp_element)
                time.sleep(1.5)

                # CAPTURA DA URL EXATA DA COMPETIÇÃO
                comp_url: str = self.driver.current_url

                matches = self._parse_matches_from_page()
                self.driver.back()

                return matches, comp_url  # Agora retorna a Tupla

            except Exception as e:
                console.print(
                    f"  [warning][Aviso] Falha ao carregar '{comp_name}' (Tentativa {attempt}/{max_retries}). Motivo: {type(e).__name__}[/warning]")
                self.driver.get(self.base_url)
                time.sleep(2)

        console.print(f"  [danger][Erro] Competição '{comp_name}' ignorada após {max_retries} tentativas falhas.[/danger]")
        return [], ""

    def _parse_matches_from_page(self) -> List[Match]:
        """
        Varre a DOM da página da competição em busca de partidas.
        Faz scroll automático para capturar listas virtualizadas e
        lida com partidas Ao Vivo e Pré-jogo estruturalmente.
        """
        # Usamos um dict para garantir que não haverá duplicatas se o scroll ler o mesmo jogo duas vezes
        matches_dict: Dict[str, Match] = {}

        try:
            # Novo XPath estrutural: Pega qualquer linha que tenha a div de times (flex-1) e a de odds (flex-2)
            # Isso ignora se o jogo é PreEvent ou "undefined--line" (Ao Vivo)
            xpath_any_match_row = "//div[div[contains(@class, 'flex-1')] and div[contains(@class, 'flex-2')]]"

            try:
                # Aguarda a estrutura de jogos carregar
                DriverUtils.wait_presence_by_xpath(self.driver, xpath_any_match_row, timeout=15)
            except:
                # Se der timeout, a competição realmente não tem jogos abertos no momento
                return []

            # Inicia o loop de varredura com Scroll
            while True:
                match_elements = self.driver.find_elements(By.XPATH, xpath_any_match_row)

                for match_el in match_elements:
                    try:
                        team_spans = match_el.find_elements(By.XPATH,
                                                            ".//span[contains(@class, 'text-[12px]') and contains(@class, 'font-sans-bold')]")
                        if len(team_spans) < 2:
                            continue

                        home_team = team_spans[0].get_attribute("textContent").strip()
                        away_team = team_spans[1].get_attribute("textContent").strip()
                        match_id = f"{home_team} x {away_team}"

                        if match_id in matches_dict:
                            continue

                        match_time = "Indefinido"

                        time_spans = match_el.find_elements(By.XPATH, ".//span[contains(@class, 'mui-1kkvss8')]")
                        if time_spans:
                            match_time = time_spans[0].get_attribute("textContent").strip()
                        else:
                            live_indicator = match_el.find_elements(By.XPATH, ".//span[contains(text(), 'Ao vivo')]")
                            if live_indicator:
                                timer_spans = match_el.find_elements(By.XPATH,
                                                                     ".//span[contains(@class, 'mui-15r481u')]")
                                if timer_spans:
                                    timer_text = " ".join([t.get_attribute("textContent").strip() for t in timer_spans])
                                    match_time = f"Ao vivo ({timer_text})"
                                else:
                                    match_time = "Ao vivo"

                        matches_dict[match_id] = Match(
                            home_team=home_team,
                            away_team=away_team,
                            datetime=match_time
                        )

                    except Exception:
                        continue

                self.driver.execute_script("window.scrollBy(0, 800);")
                time.sleep(0.5)

                # 4. Cálculo para saber se chegou ao fim da página
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                current_scroll = self.driver.execute_script("return window.pageYOffset + window.innerHeight")

                if current_scroll >= new_height:
                    # Dá um pequeno delay e checa novamente para evitar falsos positivos de lazy loading
                    time.sleep(1)
                    current_scroll = self.driver.execute_script("return window.pageYOffset + window.innerHeight")
                    new_height = self.driver.execute_script("return document.body.scrollHeight")
                    if current_scroll >= new_height:
                        break

            # Por garantia, sobe a página toda de volta pro topo para não quebrar cliques futuros
            self.driver.execute_script("window.scrollTo(0, 0);")

        except Exception as e:
            console.print(f"[danger]Erro inesperado no parse dos jogos: {e}[/danger]")

        # Retorna apenas a lista de valores (os objetos Match)
        return list(matches_dict.values())
