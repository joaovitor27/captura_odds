"""
Módulo Principal - Captura de Odds (Rei do Pitaco)

Coordena a inicialização do navegador customizado, a raspagem de dados nas páginas 
de competições e de jogos, o acúmulo de dados de mercados (como odds e resultados finais) 
e a exportação consolidada dessas informações para banco de dados e arquivos Excel.
"""
from datetime import datetime
from typing import List
import pandas as pd

from chromium import CustomWebDriver
from database.connection import DatabaseManager
from database.repositories.competition_repository import CompetitionRepository
from database.repositories.resultado_final_repository import ResultadoFinalRepository
from database.repositories.total_gols_repository import TotalGolsRepository
from driver import DriverUtils
from models.rei_do_pitaco.base_models import Competition
from scrapers.rei_do_pitaco_scraper import ReiDoPitacoScraper, ReiDoPitacoMarketExplorer
from strategies.resultado_final_strategy import ResultadoFinalStrategy
from strategies.strategies import MarketStrategy
from strategies.total_gols_strategy import TotalGolsStrategy
from utils.logger import console, clear_screen
from rich.panel import Panel
from rich.prompt import Prompt

if __name__ == '__main__':
    db_manager = DatabaseManager()
    comp_repo = CompetitionRepository(db_manager)
    
    available_strategies = [
        ("Resultado Final", ResultadoFinalStrategy(ResultadoFinalRepository(db_manager))),
        ("Total de Gols", TotalGolsStrategy(TotalGolsRepository(db_manager))),
    ]

    competitions_data: List[Competition] = comp_repo.get_all()
    driver: CustomWebDriver = DriverUtils.new_driver(headless=False)

    try:
        clear_screen()
        console.print(Panel("[bold highlight]Captura de Odds Rei do Pitaco[/bold highlight]\n[dim]Iniciando sistema de automação...[/dim]", style="cyan"))
        
        # --- SELEÇÃO DE MERCADOS ---
        console.print("\n[highlight]Mercados Disponíveis:[/highlight]")
        for i, (name, _) in enumerate(available_strategies, 1):
            console.print(f"  [cyan][{i}][/cyan] {name}")
        
        market_choice = Prompt.ask(
            "\nEscolha os mercados para capturar (ex: 1, 1,2 ou 'todos')",
            default="todos"
        ).strip().lower()

        strategies: List[MarketStrategy] = []
        if market_choice == 'todos':
            strategies = [strategy for _, strategy in available_strategies]
        else:
            try:
                indices = [int(idx.strip()) - 1 for idx in market_choice.split(',')]
                strategies = [available_strategies[i][1] for i in indices if 0 <= i < len(available_strategies)]
            except ValueError:
                console.print("[warning]Entrada inválida. Utilizando todos os mercados por padrão.[/warning]")
                strategies = [strategy for _, strategy in available_strategies]

        if not strategies:
            console.print("[danger]Nenhum mercado selecionado. Encerrando.[/danger]")
            driver.quit()
            exit(0)

        scraper = ReiDoPitacoScraper(driver)
        
        is_from_db = bool(competitions_data)

        if not is_from_db:
            with console.status("[info]Banco de dados vazio. Iniciando Mapeamento (Fase 1)...[/info]", spinner="point"):
                competitions_data = scraper.scrape_all_unique_competitions()

            console.print(f"[success]✔️ Mapeamento de {len(competitions_data)} competições concluído. Salvando...[/success]")
            with console.status("[info]Salvando competições...[/info]"):
                comp_repo.save_all(competitions_data)
        else:
            console.print(f"[success]✔️ Encontradas {len(competitions_data)} competições no banco de dados![/success]")
            console.print("[dim]Pulando mapeamento de estrutura e utilizando URLs diretas.[/dim]")

        # --- SELEÇÃO DE COMPETIÇÕES ---
        console.print("\n[highlight]Competições Disponíveis:[/highlight]")
        for i, comp in enumerate(competitions_data, 1):
            console.print(f"  [cyan][{i}][/cyan] {comp.name}")
        
        comp_choice = Prompt.ask(
            "\nEscolha as competições para mapear (ex: 1, 1,3,4 ou 'todos')",
            default="todos"
        ).strip().lower()

        selected_competitions: List[Competition] = []
        if comp_choice == 'todos':
            selected_competitions = competitions_data
        else:
            try:
                indices = [int(idx.strip()) - 1 for idx in comp_choice.split(',')]
                selected_competitions = [competitions_data[i] for i in indices if 0 <= i < len(competitions_data)]
            except ValueError:
                console.print("[warning]Entrada inválida. Utilizando todas as competições por padrão.[/warning]")
                selected_competitions = competitions_data

        if not selected_competitions:
            console.print("[danger]Nenhuma competição selecionada. Encerrando.[/danger]")
            driver.quit()
            exit(0)

        if is_from_db:
            with console.status("[info]Atualizando jogos em cache...[/info]", spinner="point"):
                scraper.refresh_matches_from_urls(selected_competitions)

        console.print(Panel("[highlight]Iniciando Exploração de Mercados (Fase 2)[/highlight]", style="cyan"))
        market_explorer = ReiDoPitacoMarketExplorer(driver, strategies)
        
        with console.status("[warning]Escaneando odds ativas... (Isso pode levar alguns minutos)[/warning]", spinner="bouncingBar"):
            mercados_encontrados = market_explorer.discover_unique_markets(selected_competitions)
            
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
                
                if not writer.sheets:
                    pd.DataFrame({'Aviso': ['Nenhum dado capturado nesta execução.']}).to_excel(writer, sheet_name="Sem Dados", index=False)

        console.print(f"[success]✅ Relatório Excel gerado com sucesso: [bold]{filename}[/bold][/success]")
        console.print(Panel("[bold green]Processo finalizado! O programa já pode ser fechado.[/bold green]"))

    except Exception as e:
        console.print_exception()
        console.print(f"\n[danger][ERRO CRÍTICO] Falha durante a execução: {e}[/danger]")

    finally:
        console.print("[dim]Encerrando driver...[/dim]")
        driver.quit()