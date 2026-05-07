from database.connection import DatabaseManager
from database.repositories.base_repository import BaseRepository
from models.rei_do_pitaco.finalizacoes_gol import FinalizacoesGolMarket

class FinalizacoesGolRepository(BaseRepository[FinalizacoesGolMarket]):
    """Isola a lógica de persistência do mercado de Finalizações no Gol."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        super().__init__(db_manager, FinalizacoesGolMarket, "finalizacoes_gol")
        self.clear_table()
