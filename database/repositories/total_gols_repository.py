from database.connection import DatabaseManager
from database.repositories.base_repository import BaseRepository
from models.rei_do_pitaco.total_gols import TotalGolsMarket

class TotalGolsRepository(BaseRepository[TotalGolsMarket]):
    """Isola a lógica de persistência do mercado de Total de Gols."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        super().__init__(db_manager, TotalGolsMarket, "total_gols")
        self.clear_table()