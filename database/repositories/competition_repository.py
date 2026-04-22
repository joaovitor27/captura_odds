from typing import List

from database.connection import DatabaseManager
from database.repositories.base_repository import BaseRepository
from models.rei_do_pitado_models import Competition


class CompetitionRepository(BaseRepository[Competition]):
    """Isola a lógica de persistência das competições usando BaseRepository."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        super().__init__(db_manager, Competition, "competitions", unique_fields=["name"])

    def save_all(self, competitions: List[Competition], unique_conflict: str = "IGNORE") -> None:
        # Salva apenas se tivermos capturado a URL corretamente
        valid_competitions = [c for c in competitions if c.url]
        super().save_all(valid_competitions, unique_conflict)
