import duckdb
from abc import ABC, abstractmethod

class DuckDBConnectionFactory(ABC):
    """
    Fábrica abstrata para prover conexões do DuckDB.
    """
    @abstractmethod
    def get_connection(self) -> duckdb.DuckDBPyConnection:
        pass

class FileBasedDuckDBConnectionFactory(DuckDBConnectionFactory):
    """
    Fábrica que provê conexão com um arquivo DuckDB no disco.
    """
    def __init__(self, db_path: str):
        self.db_path = db_path

    def get_connection(self) -> duckdb.DuckDBPyConnection:
        return duckdb.connect(self.db_path)

class MemoryDuckDBConnectionFactory(DuckDBConnectionFactory):
    """
    Fábrica que provê uma conexão em memória (ideal para testes rápidos).
    """
    def __init__(self):
        self._connection = duckdb.connect(':memory:')

    def get_connection(self) -> duckdb.DuckDBPyConnection:
        return self._connection