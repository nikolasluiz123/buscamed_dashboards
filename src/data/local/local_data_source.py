from abc import ABC, abstractmethod
import duckdb
from typing import List, Optional
from datetime import timezone, datetime

from src.data.queries import ExecutionQueries
from src.domain.entities import Execution, ExecutionFilter


class LocalDataSource(ABC):
    """
    Abstração para o acesso a dados locais.
    """

    @abstractmethod
    def get_last_sync_date(self) -> Optional[str]:
        pass

    @abstractmethod
    def update_last_sync_date(self, sync_date: datetime) -> None:
        pass

    @abstractmethod
    def save_executions(self, executions: List[Execution]) -> None:
        pass

    @abstractmethod
    def get_all_executions(self, filters: Optional[ExecutionFilter] = None) -> List[Execution]:
        pass

    @abstractmethod
    def get_available_prompts(self) -> List[str]:
        pass


class DuckDBLocalDataSource(LocalDataSource):
    """
    Implementação base do LocalDataSource para DuckDB.
    """

    def __init__(self, db_path: str, execution_type: str):
        self.db_path = db_path
        self.execution_type = execution_type

    def get_last_sync_date(self) -> Optional[str]:
        """
        Obtém a data da última sincronização registrada.
        """
        with duckdb.connect(self.db_path) as con:
            result = con.execute(ExecutionQueries.GET_LAST_SYNC_DATE, [self.execution_type]).fetchone()

            if result and result[0]:
                dt = result[0]
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt.isoformat().replace("+00:00", "Z")

            return None

    def update_last_sync_date(self, sync_date: datetime) -> None:
        """
        Atualiza o registro com a data e hora do último sincronismo bem-sucedido.
        """
        with duckdb.connect(self.db_path) as con:
            con.execute(ExecutionQueries.UPSERT_SYNC_DATE, [self.execution_type, sync_date])

    def save_executions(self, executions: List[Execution]) -> None:
        if not executions:
            return

        with duckdb.connect(self.db_path) as con:
            con.execute("BEGIN TRANSACTION")
            for execution in executions:
                con.execute(ExecutionQueries.UPSERT_EXECUTION, [
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
        query = ExecutionQueries.GET_ALL_EXECUTIONS_BY_TYPE
        params = [self.execution_type]

        if filters and filters.prompt:
            query += " AND prompt = ?"
            params.append(filters.prompt)

        with duckdb.connect(self.db_path) as con:
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
        with duckdb.connect(self.db_path) as con:
            rows = con.execute(ExecutionQueries.GET_AVAILABLE_PROMPTS, [self.execution_type]).fetchall()
            return sorted([row[0] for row in rows])


class PrescriptionLocalDataSource(DuckDBLocalDataSource):
    """
    Implementação específica para dados locais de Receitas Médicas.
    """

    def __init__(self, db_path: str):
        super().__init__(db_path=db_path, execution_type="prescription")


class PillPackLocalDataSource(DuckDBLocalDataSource):
    """
    Implementação específica para dados locais de Cartelas de Comprimidos.
    """

    def __init__(self, db_path: str):
        super().__init__(db_path=db_path, execution_type="pillpack")