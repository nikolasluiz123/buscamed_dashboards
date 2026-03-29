from typing import List, Optional
from datetime import datetime

from src.data.local.local_data_source import LocalDataSource
from src.data.remote.remote_datasource import BaseAPIExecutionDataSource
from src.domain.entities import Execution, ExecutionFilter


class ExecutionRepository:
    """
    Repositório que coordena o fluxo de dados entre fontes locais e remotas para um contexto específico.
    """

    def __init__(self, local_ds: LocalDataSource, remote_ds: BaseAPIExecutionDataSource):
        self.local_ds = local_ds
        self.remote_ds = remote_ds

    def get_last_sync_date(self) -> Optional[str]:
        return self.local_ds.get_last_sync_date()

    def update_last_sync_date(self, sync_date: datetime) -> None:
        """
        Salva na fonte local a data da última operação de sincronização.
        """
        self.local_ds.update_last_sync_date(sync_date)

    async def fetch_remote_executions(self, since_date: Optional[str]) -> List[Execution]:
        return await self.remote_ds.fetch_executions(since_date)

    def save_executions(self, executions: List[Execution]) -> None:
        self.local_ds.save_executions(executions)

    def get_all_executions(self, filters: Optional[ExecutionFilter] = None) -> List[Execution]:
        return self.local_ds.get_all_executions(filters)

    def get_available_prompts(self) -> List[str]:
        """
        Recupera os prompts distintos utilizados nas execuções para o contexto deste repositório.
        """
        return self.local_ds.get_available_prompts()

    async def get_image(self, execution_id: str) -> bytes:
        """
        Busca os bytes da imagem associada a uma execução através da fonte remota pelo seu ID.
        """
        return await self.remote_ds.fetch_image(execution_id)