from typing import List

from chromium import CustomWebDriver
from database.__inti__ import DatabaseManager
from database.repositories.competition_repository import CompetitionRepository
from driver import DriverUtils
from models.rei_do_pitado_models import Competition
from scrapers.rei_do_pitaco_scraper import ReiDoPitacoScraper, ReiDoPitacoMarketExplorer

if __name__ == '__main__':
    db_manager = DatabaseManager()
    comp_repo = CompetitionRepository(db_manager)

    competitions_data: List[Competition] = comp_repo.get_all()
    driver: CustomWebDriver = DriverUtils.new_driver(headless=False)

    try:
        scraper = ReiDoPitacoScraper(driver)

        if not competitions_data:
            print("Banco de dados vazio. Iniciando Mapeamento Scraper (Fase 1)...")
            competitions_data = scraper.scrape_all_unique_competitions()

            print(f"Salvando {len(competitions_data)} competições no banco de dados SQLite...")
            comp_repo.save_all(competitions_data)
        else:
            print(f"✔️ Encontradas {len(competitions_data)} competições no banco de dados!")
            print("Pulando mapeamento de estrutura e utilizando URLs diretas.")

            # ---> O CÓDIGO QUE FALTAVA <---
            # Popula a variável "matches" de cada competição usando os links diretos
            scraper.refresh_matches_from_urls(competitions_data)

        print("\nIniciando Exploração de Mercados (Fase 2)...")
        market_explorer = ReiDoPitacoMarketExplorer(driver)
        mercados_encontrados: set[str] = market_explorer.discover_unique_markets(competitions_data)

        print("\n" + "=" * 60)
        print(f"TOTAL DE MERCADOS ÚNICOS ENCONTRADOS: {len(mercados_encontrados)}")
        print("=" * 60)

    except Exception as e:
        print(f"\n[ERRO CRÍTICO] Falha durante a execução: {e}")

    finally:
        print("\nEncerrando driver...")
        driver.quit()