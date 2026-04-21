from datetime import datetime
from typing import List
import pandas as pd

from chromium import CustomWebDriver
from database.__inti__ import DatabaseManager
from database.repositories.competition_repository import CompetitionRepository
from database.repositories.resultado_final_repository import ResultadoFinalRepository
from driver import DriverUtils
from models.rei_do_pitado_models import Competition
from scrapers.rei_do_pitaco_scraper import ReiDoPitacoScraper, ReiDoPitacoMarketExplorer
from strategies.resultado_final_strategy import ResultadoFinalStrategy
from strategies.strategies import MarketStrategy

if __name__ == '__main__':
    db_manager = DatabaseManager()
    comp_repo = CompetitionRepository(db_manager)
    strategies: List[MarketStrategy] = [
        ResultadoFinalStrategy(ResultadoFinalRepository(db_manager)),
        # TotalGolsStrategy(TotalGolsRepository(db_manager)), <-- Exemplo futuro
        # HandicapStrategy(HandicapRepository(db_manager)),   <-- Exemplo futuro
    ]

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

            scraper.refresh_matches_from_urls(competitions_data)

        print("\nIniciando Exploração de Mercados (Fase 2)...")
        market_explorer = ReiDoPitacoMarketExplorer(driver, strategies)
        mercados_encontrados = market_explorer.discover_unique_markets(competitions_data)
        print("\n" + "=" * 60)
        for strategy in strategies:
            strategy.save_to_db()
        print("=" * 60)

        print("\nGERANDO RELATÓRIO EXCEL...")
        filename = f"relatorio_odds_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            for strategy in strategies:
                strategy.export_to_excel(writer)

        print(f"✅ Arquivo gerado com sucesso: {filename}")
        print("=" * 60)

    except Exception as e:
        print(f"\n[ERRO CRÍTICO] Falha durante a execução: {e}")

    finally:
        print("\nEncerrando driver...")
        driver.quit()