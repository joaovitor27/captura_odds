from typing import List

from database.connection import DatabaseManager
from models.rei_do_pitado_models import Competition


class CompetitionRepository:
    """Isola a lógica de persistência das competições."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        self.db: DatabaseManager = db_manager
        self._create_table()

    def _create_table(self) -> None:
        query: str = """
                     CREATE TABLE IF NOT EXISTS competitions
                     (
                         id
                         INTEGER
                         PRIMARY
                         KEY
                         AUTOINCREMENT,
                         name
                         TEXT
                         UNIQUE
                         NOT
                         NULL,
                         url
                         TEXT
                         NOT
                         NULL
                     )
                     """
        with self.db.get_connection() as conn:
            conn.execute(query)

    def save_all(self, competitions: List[Competition]) -> None:
        query: str = """
                     INSERT
                     OR IGNORE INTO competitions (name, url)
        VALUES (?, ?)
                     """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            for comp in competitions:
                # Salva apenas se tivermos capturado a URL corretamente
                if comp.url:
                    cursor.execute(query, (comp.name, comp.url))

    def get_all(self) -> List[Competition]:
        query: str = "SELECT name, url FROM competitions"
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()

            # Reconstrói os objetos Competition a partir do banco
            return [Competition(name=row["name"], url=row["url"]) for row in rows]
