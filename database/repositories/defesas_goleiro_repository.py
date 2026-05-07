from database.connection import DatabaseManager
from database.repositories.base_repository import BaseRepository
from models.rei_do_pitaco.defesas_goleiro import DefesasGoleiroMarket

class DefesasGoleiroRepository(BaseRepository[DefesasGoleiroMarket]):
    """Isola a lógica de persistência do mercado de Defesas de Goleiro."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        super().__init__(db_manager, DefesasGoleiroMarket, "defesas_goleiro")
        self.clear_table()
