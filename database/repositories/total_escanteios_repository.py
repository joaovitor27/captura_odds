from database.connection import DatabaseManager
from database.repositories.base_repository import BaseRepository
from models.rei_do_pitaco.total_escanteios import TotalEscanteiosMarket

class TotalEscanteiosRepository(BaseRepository[TotalEscanteiosMarket]):
    """Isola a lógica de persistência do mercado de Total de Escanteios."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        super().__init__(db_manager, TotalEscanteiosMarket, "total_escanteios")
        self.clear_table()
