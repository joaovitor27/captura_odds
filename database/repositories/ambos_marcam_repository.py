from database.connection import DatabaseManager
from database.repositories.base_repository import BaseRepository
from models.rei_do_pitaco.ambos_marcam import AmbosMarcamMarket

class AmbosMarcamRepository(BaseRepository[AmbosMarcamMarket]):
    """Isola a lógica de persistência do mercado de Ambos Marcam."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        super().__init__(db_manager, AmbosMarcamMarket, "ambos_marcam")
        self.clear_table()
