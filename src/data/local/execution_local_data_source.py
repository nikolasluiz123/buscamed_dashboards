from abc import ABC, abstractmethod
from typing import List, Optional

from src.data.queries.query_manager import QueryManager
from src.domain.entities import Execution, ExecutionFilter
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
                    execution.input_tokens,
                    execution.output_tokens,
                    execution.result,
                    execution.success,
                    execution.start_date,
                    execution.end_date,
                    execution.storage_image_path,
                    execution.prompt
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

        if filters and filters.prompt:
            dynamic_filters += " AND prompt = ?"
            params.append(filters.prompt)

        query = query.replace("{filters}", dynamic_filters)

        with self._connection_factory.get_connection() as con:
            rows = con.execute(query, params).fetchall()

            return [
                Execution(
                    id=row[0],
                    execution_type=row[1],
                    input_tokens=row[2],
                    output_tokens=row[3],
                    result=row[4],
                    success=row[5],
                    start_date=row[6],
                    end_date=row[7],
                    storage_image_path=row[8],
                    prompt=row[9] if len(row) > 9 and row[9] is not None else ""
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