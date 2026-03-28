from typing import List, Optional

from src.data.local.local_data_source import LocalDataSource
from src.data.remote.remote_datasource import RemoteDataSource
from src.domain.entities import Execution


class ExecutionRepository:
    """
    Repositório que coordena o fluxo de dados entre fontes locais e remotas para um contexto específico.
    """

    def __init__(self, local_ds: LocalDataSource, remote_ds: RemoteDataSource):
        self.local_ds = local_ds
        self.remote_ds = remote_ds

    def get_last_sync_date(self) -> Optional[str]:
        return self.local_ds.get_last_sync_date()

    async def fetch_remote_executions(self, since_date: Optional[str]) -> List[Execution]:
        return await self.remote_ds.fetch_executions(since_date)

    def save_executions(self, executions: List[Execution]) -> None:
        self.local_ds.save_executions(executions)

    def get_all_executions(self) -> List[Execution]:
        return self.local_ds.get_all_executions()