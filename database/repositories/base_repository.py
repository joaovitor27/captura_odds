import sqlite3
from typing import TypeVar, Generic, Type, List, Any, get_origin, Dict, Optional
from dataclasses import fields, is_dataclass

from database.connection import DatabaseManager

T = TypeVar('T')

class BaseRepository(Generic[T]):
    """
    Repositório genérico que cria tabelas e gerencia operações de CRUD básicas
    utilizando Dataclasses, evitando a necessidade de escrever queries manuais.
    """

    def __init__(self, db_manager: DatabaseManager, model_class: Type[T], table_name: str, unique_fields: Optional[List[str]] = None) -> None:
        if not is_dataclass(model_class):
            raise ValueError(f"O modelo {model_class.__name__} deve ser um dataclass.")
            
        self.db = db_manager
        self.model_class = model_class
        self.table_name = table_name
        self.unique_fields = unique_fields or []
        self._fields = self._get_valid_fields()
        
        self._create_table()
        
    def _get_valid_fields(self) -> List[Any]:
        """Retorna apenas os campos que podem ser salvos no SQLite (ignora listas e etc)."""
        valid_fields = []
        for f in fields(self.model_class):
            # Ignora campos de lista (relacionamentos complexos)
            if get_origin(f.type) is list or get_origin(f.type) is List:
                continue
            valid_fields.append(f)
        return valid_fields
        
    def _map_python_type_to_sqlite(self, py_type: Type) -> str:
        """Mapeia os tipos do Python para os equivalentes do SQLite."""
        if py_type is int:
            return "INTEGER"
        elif py_type is float:
            return "REAL"
        elif py_type is bool:
            return "BOOLEAN"
        return "TEXT"

    def _create_table(self) -> None:
        """Cria a tabela no banco baseada nos campos da dataclass."""
        columns = ["id INTEGER PRIMARY KEY AUTOINCREMENT"]
        for f in self._fields:
            sqlite_type = self._map_python_type_to_sqlite(f.type)
            constraints = "UNIQUE NOT NULL" if f.name in self.unique_fields else "NOT NULL"
            columns.append(f"{f.name} {sqlite_type} {constraints}")
            
        columns_sql = ",\n            ".join(columns)
        query = f"CREATE TABLE IF NOT EXISTS {self.table_name} (\n            {columns_sql}\n        )"
        
        with self.db.get_connection() as conn:
            conn.execute(query)

    def save_all(self, items: List[T], unique_conflict: str = "IGNORE") -> None:
        """Salva uma lista de objetos no banco de forma genérica."""
        if not items:
            return
            
        field_names = [f.name for f in self._fields]
        columns_sql = ", ".join(field_names)
        placeholders = ", ".join(["?"] * len(field_names))
        
        query = f"INSERT OR {unique_conflict} INTO {self.table_name} ({columns_sql}) VALUES ({placeholders})"
        
        data_tuples = []
        for item in items:
            row = [getattr(item, f.name) for f in self._fields]
            data_tuples.append(tuple(row))
            
        with self.db.get_connection() as conn:
            conn.executemany(query, data_tuples)
            
    def get_all(self) -> List[T]:
        """Recupera todos os itens da tabela e os converte de volta para objetos Python."""
        field_names = [f.name for f in self._fields]
        columns_sql = ", ".join(field_names)
        query = f"SELECT {columns_sql} FROM {self.table_name}"
        
        results = []
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            
            for row in rows:
                kwargs = {name: row[name] for name in field_names}
                results.append(self.model_class(**kwargs))
                
        return results

    def clear_table(self) -> None:
        """Limpa todos os registros da tabela."""
        with self.db.get_connection() as conn:
            conn.execute(f"DELETE FROM {self.table_name}")
            conn.execute(f"DELETE FROM sqlite_sequence WHERE name='{self.table_name}'")
