from typing import List

from database.__inti__ import DatabaseManager
from models.rei_do_pitado_models import ResultadoFinalMarket


class ResultadoFinalRepository:
    def __init__(self, db_manager: DatabaseManager) -> None:
        self.db: DatabaseManager = db_manager
        self._create_table()
        self.clear_table()  # Garante dados atualizados a cada execução do script

    def _create_table(self) -> None:
        query: str = """
                     CREATE TABLE IF NOT EXISTS resultado_final
                     (
                         id
                         INTEGER
                         PRIMARY
                         KEY
                         AUTOINCREMENT,
                         competicao
                         TEXT
                         NOT
                         NULL,
                         partida
                         TEXT
                         NOT
                         NULL,
                         data
                         TEXT
                         NOT
                         NULL,
                         hora
                         TEXT
                         NOT
                         NULL,
                         time_casa
                         TEXT
                         NOT
                         NULL,
                         time_fora
                         TEXT
                         NOT
                         NULL,
                         odd_time_casa
                         REAL
                         NOT
                         NULL,
                         odd_time_fora
                         REAL
                         NOT
                         NULL,
                         odd_empate
                         REAL
                         NOT
                         NULL,
                         is_pagamento_antecipado
                         BOOLEAN
                         NOT
                         NULL
                     ) \
                     """
        with self.db.get_connection() as conn:
            conn.execute(query)

    def clear_table(self) -> None:
        """Deleta todos os dados antigos da tabela."""
        with self.db.get_connection() as conn:
            conn.execute("DELETE FROM resultado_final")
            # Reseta o autoincrement do SQLite (opcional, mas mantém a base limpa)
            conn.execute("DELETE FROM sqlite_sequence WHERE name='resultado_final'")

    def save_all(self, markets: List[ResultadoFinalMarket]) -> None:
        if not markets:
            return

        query: str = """
                     INSERT INTO resultado_final
                     (competicao, partida, data, hora, time_casa, time_fora, odd_time_casa, odd_time_fora, odd_empate,
                      is_pagamento_antecipado)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) \
                     """

        # Converte a listagem de objetos para tuplas no formato do banco
        data_tuples = [
            (
                m.competicao, m.partida, m.data, m.hora,
                m.time_casa, m.time_fora, m.odd_time_casa, m.odd_time_fora, m.odd_empate,
                m.is_pagamento_antecipado
            )
            for m in markets
        ]

        with self.db.get_connection() as conn:
            conn.executemany(query, data_tuples)
