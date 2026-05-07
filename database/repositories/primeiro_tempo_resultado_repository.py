from database.connection import DatabaseManager
from database.repositories.base_repository import BaseRepository
from models.rei_do_pitaco.primeiro_tempo_resultado import PrimeiroTempoResultadoMarket

class PrimeiroTempoResultadoRepository(BaseRepository[PrimeiroTempoResultadoMarket]):
    """Isola a lógica de persistência do mercado de 1º Tempo - Resultado."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        super().__init__(db_manager, PrimeiroTempoResultadoMarket, "primeiro_tempo_resultado")
        self.clear_table()
