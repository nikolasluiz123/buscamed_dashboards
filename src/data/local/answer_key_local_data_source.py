import json
from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.entities import AnswerKey
from src.data.local.connection_factory import DuckDBConnectionFactory
from src.data.queries.query_manager import QueryManager


class AnswerKeyLocalDataSource(ABC):
    """
    Abstração para o acesso a dados locais de gabaritos.
    """

    @abstractmethod
    def save(self, answer_key: AnswerKey) -> AnswerKey:
        pass

    @abstractmethod
    def get_all(self, document_type: Optional[str] = None) -> List[AnswerKey]:
        pass

    @abstractmethod
    def get_by_execution_id(self, execution_id: str) -> Optional[AnswerKey]:
        pass

    @abstractmethod
    def delete(self, answer_key_id: int) -> None:
        pass


class DuckDBAnswerKeyLocalDataSource(AnswerKeyLocalDataSource):
    """
    Implementação do AnswerKeyLocalDataSource para DuckDB.
    """

    def __init__(self, connection_factory: DuckDBConnectionFactory, query_manager: QueryManager):
        self._connection_factory = connection_factory
        self._query_manager = query_manager

    def save(self, answer_key: AnswerKey) -> AnswerKey:
        """
        Insere ou atualiza um gabarito no banco de dados.
        """
        query = self._query_manager.get('upsert_answer_key')
        content_json = json.dumps(answer_key.content)

        with self._connection_factory.get_connection() as con:
            result = con.execute(
                query,
                [answer_key.id, answer_key.execution_id, answer_key.document_type, content_json]
            ).fetchone()

            answer_key.id = result[0]
            answer_key.created_at = result[1]
            return answer_key

    def get_all(self, document_type: Optional[str] = None) -> List[AnswerKey]:
        """
        Recupera os gabaritos, opcionalmente filtrando por tipo de documento.
        """
        query = self._query_manager.get('get_all_answer_keys')
        params = []
        dynamic_filters = ""

        if document_type:
            dynamic_filters = "WHERE document_type = ?"
            params.append(document_type)

        query = query.replace("{filters}", dynamic_filters)

        with self._connection_factory.get_connection() as con:
            rows = con.execute(query, params).fetchall()

            return [
                AnswerKey(
                    id=row[0],
                    execution_id=row[1],
                    document_type=row[2],
                    content=json.loads(row[3]),
                    created_at=row[4]
                ) for row in rows
            ]

    def get_by_execution_id(self, execution_id: str) -> Optional[AnswerKey]:
        """
        Busca um gabarito específico vinculado a uma execução.
        """
        query = self._query_manager.get('get_answer_key_by_execution_id')

        with self._connection_factory.get_connection() as con:
            row = con.execute(query, [execution_id]).fetchone()

            if not row:
                return None

            return AnswerKey(
                id=row[0],
                execution_id=row[1],
                document_type=row[2],
                content=json.loads(row[3]),
                created_at=row[4]
            )

    def delete(self, answer_key_id: int) -> None:
        """
        Remove um gabarito do banco de dados.
        """
        query = self._query_manager.get('delete_answer_key')

        with self._connection_factory.get_connection() as con:
            con.execute(query, [answer_key_id])