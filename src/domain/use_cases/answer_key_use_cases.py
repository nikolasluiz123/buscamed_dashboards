from typing import List, Optional

from src.data.repositories import AnswerKeyRepository
from src.domain.entities import AnswerKey


class ManageAnswerKeyUseCase:
    """
    Caso de uso responsável pelas operações de escrita e deleção de gabaritos.
    """

    def __init__(self, repository: AnswerKeyRepository):
        self._repository = repository

    def save(self, execution_id: str, document_type: str, content: dict,
             answer_key_id: Optional[int] = None) -> AnswerKey:
        """
        Cria ou atualiza a entidade de gabarito e solicita sua persistência.
        """
        answer_key = AnswerKey(
            id=answer_key_id,
            execution_id=execution_id,
            document_type=document_type,
            content=content
        )
        return self._repository.save_answer_key(answer_key)

    def delete(self, answer_key_id: int) -> None:
        """
        Solicita a deleção de um gabarito.
        """
        self._repository.delete_answer_key(answer_key_id)


class GetAnswerKeysUseCase:
    """
    Caso de uso responsável pelas consultas de gabaritos.
    """

    def __init__(self, repository: AnswerKeyRepository):
        self._repository = repository

    def get_all(self, document_type: Optional[str] = None) -> List[AnswerKey]:
        """
        Recupera a lista de gabaritos.
        """
        return self._repository.get_answer_keys(document_type)

    def get_by_execution(self, execution_id: str) -> Optional[AnswerKey]:
        """
        Recupera o gabarito associado a uma execução.
        """
        return self._repository.get_answer_key_by_execution(execution_id)