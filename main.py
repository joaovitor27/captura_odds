from datetime import datetime
from typing import List
import pandas as pd

from chromium import CustomWebDriver
from database.connection import DatabaseManager
from database.repositories.competition_repository import CompetitionRepository
from database.repositories.resultado_final_repository import ResultadoFinalRepository
from driver import DriverUtils
from models.rei_do_pitado_models import Competition
from scrapers.rei_do_pitaco_scraper import ReiDoPitacoScraper, ReiDoPitacoMarketExplorer
from strategies.resultado_final_strategy import ResultadoFinalStrategy
from strategies.strategies import MarketStrategy
from utils.logger import console, clear_screen
from rich.panel import Panel

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
        clear_screen()
        console.print(Panel("[bold highlight]Captura de Odds Rei do Pitaco[/bold highlight]\n[dim]Iniciando sistema de automação...[/dim]", style="cyan"))
        
        scraper = ReiDoPitacoScraper(driver)

        if not competitions_data:
            with console.status("[info]Banco de dados vazio. Iniciando Mapeamento (Fase 1)...[/info]", spinner="point"):
                competitions_data = scraper.scrape_all_unique_competitions()

            console.print(f"[success]✔️ Mapeamento de {len(competitions_data)} competições concluído. Salvando...[/success]")
            with console.status("[info]Salvando competições...[/info]"):
                comp_repo.save_all(competitions_data)
        else:
            console.print(f"[success]✔️ Encontradas {len(competitions_data)} competições no banco de dados![/success]")
            console.print("[dim]Pulando mapeamento de estrutura e utilizando URLs diretas.[/dim]")

            with console.status("[info]Atualizando jogos em cache...[/info]", spinner="point"):
                scraper.refresh_matches_from_urls(competitions_data)

        console.print(Panel("[highlight]Iniciando Exploração de Mercados (Fase 2)[/highlight]", style="cyan"))
        market_explorer = ReiDoPitacoMarketExplorer(driver, strategies)
        
        with console.status("[warning]Escaneando odds ativas... (Isso pode levar alguns minutos)[/warning]", spinner="bouncingBar"):
            mercados_encontrados = market_explorer.discover_unique_markets(competitions_data)
            
        console.print("[success]Escaneamento concluído![/success]")
        with console.status("[info]Registrando resultados na base local...[/info]"):
            for strategy in strategies:
                strategy.save_to_db()

        console.print("\n[highlight]GERANDO RELATÓRIO EXCEL...[/highlight]")
        filename = f"relatorio_odds_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        with console.status("[info]Construindo planilha...[/info]"):
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                for strategy in strategies:
                    strategy.export_to_excel(writer)

        console.print(f"[success]✅ Relatório Excel gerado com sucesso: [bold]{filename}[/bold][/success]")
        console.print(Panel("[bold green]Processo finalizado! O programa já pode ser fechado.[/bold green]"))

    except Exception as e:
        console.print_exception()
        console.print(f"\n[danger][ERRO CRÍTICO] Falha durante a execução: {e}[/danger]")

    finally:
        console.print("[dim]Encerrando driver...[/dim]")
        driver.quit()