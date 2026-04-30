from database.connection import DatabaseManager
from database.repositories.base_repository import BaseRepository
from models.rei_do_pitaco.dupla_chance import DuplaChanceMarket

class DuplaChanceRepository(BaseRepository[DuplaChanceMarket]):
    """Isola a lógica de persistência do mercado de Dupla Chance."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        super().__init__(db_manager, DuplaChanceMarket, "dupla_chance")
        self.clear_table()
