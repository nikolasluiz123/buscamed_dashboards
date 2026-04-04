import json
from typing import List, Optional

from src.domain.entities import AnswerKey, Execution
from src.domain.use_cases.answer_key_use_cases import ManageAnswerKeyUseCase, GetAnswerKeysUseCase
from src.domain.use_cases.get_image_use_case import GetImageUseCase
from src.data.repositories import ExecutionRepository


class AnswerKeysViewModel:
    """
    ViewModel responsável por intermediar as interações da tela de Gabaritos com os casos de uso.
    """

    def __init__(
            self,
            manage_use_case: ManageAnswerKeyUseCase,
            get_use_case: GetAnswerKeysUseCase,
            prescription_repository: ExecutionRepository,
            pill_pack_repository: ExecutionRepository,
            get_image_use_case: GetImageUseCase
    ):
        self._manage_use_case = manage_use_case
        self._get_use_case = get_use_case
        self._prescription_repository = prescription_repository
        self._pill_pack_repository = pill_pack_repository
        self._get_image_use_case = get_image_use_case

    def get_all_answer_keys(self, document_type: Optional[str] = None) -> List[AnswerKey]:
        """
        Recupera todos os gabaritos cadastrados.
        """
        return self._get_use_case.get_all(document_type)

    def get_pending_executions(self, document_type: str) -> List[Execution]:
        """
        Recupera as execuções de um determinado tipo que ainda não possuem gabarito associado.
        """
        repo = self._prescription_repository if document_type == "prescription" else self._pill_pack_repository
        return repo.get_executions_without_answer_keys()

    async def get_execution_image(self, execution_id: str) -> bytes:
        """
        Recupera os bytes da imagem associada à execução.
        """
        return await self._get_image_use_case.execute(execution_id)

    def save_answer_key(self, execution_id: str, document_type: str, content_str: str,
                        answer_key_id: Optional[int] = None) -> None:
        """
        Salva ou atualiza um gabarito.
        """
        content_dict = json.loads(content_str)
        self._manage_use_case.save(
            execution_id=execution_id,
            document_type=document_type,
            content=content_dict,
            answer_key_id=answer_key_id
        )

    def delete_answer_key(self, answer_key_id: int) -> None:
        """
        Remove um gabarito.
        """
        self._manage_use_case.delete(answer_key_id)