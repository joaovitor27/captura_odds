from database.connection import DatabaseManager
from database.repositories.base_repository import BaseRepository
from models.rei_do_pitaco.resultado_final import ResultadoFinalMarket


class ResultadoFinalRepository(BaseRepository[ResultadoFinalMarket]):
    """Isola a lógica de persistência do mercado de Resultado Final usando BaseRepository."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        super().__init__(db_manager, ResultadoFinalMarket, "resultado_final")
        self.clear_table()  # Garante dados atualizados a cada execução do script
