from typing import List, Optional
from datetime import datetime

from src.data.local.answer_key_local_data_source import AnswerKeyLocalDataSource
from src.data.local.sync_local_data_source import SyncLocalDataSource
from src.data.local.execution_local_data_source import ExecutionLocalDataSource
from src.data.remote.remote_datasource import ExecutionRemoteDataSource
from src.domain.entities import Execution, ExecutionFilter, AnswerKey


class ExecutionRepository:
    """
    Repositório que coordena o fluxo de dados entre fontes locais e remotas para um contexto específico.
    """

    def __init__(self,
                 sync_local_ds: SyncLocalDataSource,
                 execution_local_ds: ExecutionLocalDataSource,
                 remote_ds: ExecutionRemoteDataSource):
        self._sync_local_ds = sync_local_ds
        self._execution_local_ds = execution_local_ds
        self._remote_ds = remote_ds

    def get_last_sync_date(self) -> Optional[datetime]:
        """
        Retorna a data do último sincronismo como objeto datetime.
        """
        return self._sync_local_ds.get_last_sync_date()

    def update_last_sync_date(self, sync_date: datetime) -> None:
        """
        Salva na fonte local a data da última operação de sincronização.
        """
        self._sync_local_ds.update_last_sync_date(sync_date)

    async def fetch_remote_executions(self, since_date: Optional[datetime]) -> List[Execution]:
        """
        Busca execuções remotas delegando a formatação e busca à fonte remota.
        """
        return await self._remote_ds.fetch_executions(since_date)

    def save_executions(self, executions: List[Execution]) -> None:
        """
        Persiste as execuções obtidas na base local.
        """
        self._execution_local_ds.save_executions(executions)

    def get_all_executions(self, filters: Optional[ExecutionFilter] = None) -> List[Execution]:
        """
        Recupera todas as execuções locais de acordo com os filtros.
        """
        return self._execution_local_ds.get_all_executions(filters)

    def get_available_prompts(self) -> List[str]:
        """
        Recupera os prompts distintos utilizados nas execuções para o contexto deste repositório.
        """
        return self._execution_local_ds.get_available_prompts()

    async def get_image(self, execution_id: str) -> bytes:
        """
        Busca os bytes da imagem associada a uma execução através da fonte remota pelo seu ID.
        """
        return await self._remote_ds.fetch_image(execution_id)

    def get_available_client_processor_versions(self) -> List[str]:
        """
        Recupera as versões distintas do client processor utilizadas nas execuções.
        """
        return self._execution_local_ds.get_available_client_processor_versions()

    def get_available_llm_models(self) -> List[str]:
        """
        Recupera os modelos LLM distintos utilizados nas execuções para o contexto deste repositório.
        """
        return self._execution_local_ds.get_available_llm_models()

    def get_executions_without_answer_keys(self) -> List[Execution]:
        """
        Recupera as execuções locais que não estão vinculadas a um gabarito.
        """
        return self._execution_local_ds.get_executions_without_answer_keys()

    def get_execution_by_id(self, execution_id: str) -> Optional[Execution]:
        """
        Busca uma execução registrada localmente através do seu ID.

        Args:
            execution_id (str): Identificador único.

        Returns:
            Optional[Execution]: Instância da entidade procurada ou None caso não exista.
        """
        return self._execution_local_ds.get_execution_by_id(execution_id)

class AnswerKeyRepository:
    """
    Repositório para manipulação de gabaritos.
    """

    def __init__(self, local_ds: AnswerKeyLocalDataSource):
        self._local_ds = local_ds

    def save_answer_key(self, answer_key: AnswerKey) -> AnswerKey:
        """
        Persiste um gabarito.
        """
        return self._local_ds.save(answer_key)

    def get_answer_keys(self, document_type: Optional[str] = None) -> List[AnswerKey]:
        """
        Recupera os gabaritos disponíveis.
        """
        return self._local_ds.get_all(document_type)

    def get_answer_key_by_execution(self, execution_id: str) -> Optional[AnswerKey]:
        """
        Busca o gabarito de uma execução específica.
        """
        return self._local_ds.get_by_execution_id(execution_id)

    def delete_answer_key(self, answer_key_id: int) -> None:
        """
        Exclui um gabarito pelo seu identificador único.
        """
        self._local_ds.delete(answer_key_id)