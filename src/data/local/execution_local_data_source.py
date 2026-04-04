from abc import ABC, abstractmethod
from typing import List, Optional

from src.data.queries.query_manager import QueryManager
from src.domain.entities import Execution, ExecutionFilter, ExecutionType
from src.data.local.connection_factory import DuckDBConnectionFactory


class ExecutionLocalDataSource(ABC):
    """
    Abstração para o acesso a dados locais de execuções.
    """

    @abstractmethod
    def save_executions(self, executions: List[Execution]) -> None:
        pass

    @abstractmethod
    def get_all_executions(self, filters: Optional[ExecutionFilter] = None) -> List[Execution]:
        pass

    @abstractmethod
    def get_available_prompts(self) -> List[str]:
        pass

    @abstractmethod
    def get_available_client_processor_versions(self) -> List[str]:
        pass

    @abstractmethod
    def get_available_llm_models(self) -> List[str]:
        pass


class DuckDBExecutionLocalDataSource(ExecutionLocalDataSource):
    """
    Implementação do ExecutionLocalDataSource para DuckDB.
    """

    def __init__(self, connection_factory: DuckDBConnectionFactory, query_manager: QueryManager, execution_type: str):
        self._connection_factory = connection_factory
        self._query_manager = query_manager
        self._execution_type = execution_type

    def save_executions(self, executions: List[Execution]) -> None:
        """
        Salva uma lista de execuções no banco local.
        """
        if not executions:
            return

        with self._connection_factory.get_connection() as con:
            con.execute("BEGIN TRANSACTION")
            query = self._query_manager.get('upsert_execution')

            for execution in executions:
                con.execute(query, [
                    execution.id,
                    execution.execution_type,
                    execution.processing_type.value,
                    execution.input_text,
                    execution.input_tokens,
                    execution.output_tokens,
                    execution.result,
                    execution.success,
                    execution.start_date,
                    execution.end_date,
                    execution.storage_image_path,
                    execution.prompt,
                    execution.client_processor_version,
                    execution.llm_model
                ])
            con.execute("COMMIT")

    def get_all_executions(self, filters: Optional[ExecutionFilter] = None) -> List[Execution]:
        """
        Recupera as execuções salvas com base nos filtros fornecidos.

        Args:
            filters (Optional[ExecutionFilter]): Parâmetros de filtro opcionais. O padrão é None.

        Returns:
            List[Execution]: Uma lista de entidades de execução recuperadas do banco de dados.
        """
        query = self._query_manager.get('get_all_executions_by_type')
        params = [self._execution_type]
        dynamic_filters = ""

        if filters:
            if filters.prompt:
                dynamic_filters += " AND prompt = ?"
                params.append(filters.prompt)

            if filters.processing_type:
                dynamic_filters += " AND processing_type = ?"
                params.append(filters.processing_type.value)

            if filters.client_processor_version:
                dynamic_filters += " AND client_processor_version = ?"
                params.append(filters.client_processor_version)
            
            if filters.llm_model:
                dynamic_filters += " AND llm_model = ?"
                params.append(filters.llm_model)

        query = query.replace("{filters}", dynamic_filters)

        with self._connection_factory.get_connection() as con:
            rows = con.execute(query, params).fetchall()

            return [
                Execution(
                    id=row[0],
                    execution_type=row[1],
                    processing_type=ExecutionType(row[2]),
                    input_text=row[3],
                    input_tokens=row[4],
                    output_tokens=row[5],
                    result=row[6],
                    success=row[7],
                    start_date=row[8],
                    end_date=row[9],
                    storage_image_path=row[10],
                    prompt=row[11] if len(row) > 11 and row[11] is not None else "",
                    client_processor_version=row[12] if len(row) > 12 and row[12] is not None else "",
                    llm_model=row[13] if len(row) > 13 and row[13] is not None else ""
                ) for row in rows
            ]

    def get_available_prompts(self) -> List[str]:
        """
        Busca os diferentes prompts utilizados nas execuções.
        """
        with self._connection_factory.get_connection() as con:
            query = self._query_manager.get('get_available_prompts')
            rows = con.execute(query, [self._execution_type]).fetchall()
            return sorted([row[0] for row in rows])

    def get_available_client_processor_versions(self) -> List[str]:
        """
        Busca as diferentes versões de processador de cliente utilizadas nas execuções.
        """
        with self._connection_factory.get_connection() as con:
            query = self._query_manager.get('get_available_client_processor_versions')
            rows = con.execute(query, [self._execution_type]).fetchall()
            return sorted([row[0] for row in rows])

    def get_available_llm_models(self) -> List[str]:
        """
        Busca os diferentes modelos LLM utilizados nas execuções.
        """
        with self._connection_factory.get_connection() as con:
            query = self._query_manager.get('get_available_llm_models')
            rows = con.execute(query, [self._execution_type]).fetchall()
            return sorted([row[0] for row in rows])