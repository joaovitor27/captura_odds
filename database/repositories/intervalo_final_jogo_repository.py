from database.connection import DatabaseManager
from database.repositories.base_repository import BaseRepository
from models.rei_do_pitaco.intervalo_final_jogo import IntervaloFinalJogoMarket

class IntervaloFinalJogoRepository(BaseRepository[IntervaloFinalJogoMarket]):
    """Isola a lógica de persistência do mercado de Intervalo/Final do Jogo."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        super().__init__(db_manager, IntervaloFinalJogoMarket, "intervalo_final_jogo")
        self.clear_table()
