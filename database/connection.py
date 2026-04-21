import sqlite3
from contextlib import contextmanager
from typing import Generator


class DatabaseManager:
    """Gerencia a conexão com o banco de dados SQLite."""

    def __init__(self, db_name: str = "reidopitaco.db") -> None:
        self.db_name: str = db_name

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        conn: sqlite3.Connection = sqlite3.connect(self.db_name)
        # Permite acessar as colunas pelo nome (ex: row["name"])
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.commit()
            conn.close()