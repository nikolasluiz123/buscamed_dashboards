from abc import ABC, abstractmethod
from typing import Optional
from datetime import timezone, datetime

from src.data.local.connection_factory import DuckDBConnectionFactory
from src.data.queries.query_manager import QueryManager


class SyncLocalDataSource(ABC):
    """
    Abstração para o acesso a dados locais de controle de sincronização.
    """
    @abstractmethod
    def get_last_sync_date(self) -> Optional[datetime]:
        pass

    @abstractmethod
    def update_last_sync_date(self, sync_date: datetime) -> None:
        pass


class DuckDBSyncLocalDataSource(SyncLocalDataSource):
    """
    Implementação do SyncLocalDataSource para DuckDB.
    """
    def __init__(self, connection_factory: DuckDBConnectionFactory, query_manager: QueryManager, execution_type: str):
        self._connection_factory = connection_factory
        self._query_manager = query_manager
        self._execution_type = execution_type

    def get_last_sync_date(self) -> Optional[datetime]:
        """
        Obtém a data da última sincronização registrada como um objeto datetime com timezone.
        """
        with self._connection_factory.get_connection() as con:
            query = self._query_manager.get('get_last_sync_date')
            result = con.execute(query, [self._execution_type]).fetchone()

            if result and result[0]:
                dt = result[0]
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt

            return None

    def update_last_sync_date(self, sync_date: datetime) -> None:
        """
        Atualiza o registro com a data e hora do último sincronismo bem-sucedido.
        """
        with self._connection_factory.get_connection() as con:
            query = self._query_manager.get('upsert_sync_date')
            con.execute(query, [self._execution_type, sync_date])