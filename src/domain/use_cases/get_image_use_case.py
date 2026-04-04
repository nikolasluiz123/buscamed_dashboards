from typing import Union
from src.data.repositories import ExecutionRepository
from src.domain.entities import Execution


class GetImageUseCase:
    """
    Caso de uso para obter os bytes de uma imagem a partir de uma execução ou do seu identificador.
    """

    def __init__(self, prescription_repository: ExecutionRepository, pill_pack_repository: ExecutionRepository):
        self.prescription_repository = prescription_repository
        self.pill_pack_repository = pill_pack_repository

    async def execute(self, execution_or_id: Union[Execution, str]) -> bytes:
        """
        Recupera os bytes da imagem vinculada à execução informada.

        Args:
            execution_or_id (Union[Execution, str]): Entidade Execution ou seu identificador único (str).

        Returns:
            bytes: Conteúdo binário da imagem recuperada da origem.

        Raises:
            ValueError: Lançado caso a execução não seja localizada pelo ID fornecido ou não possua imagem definida.
        """
        if isinstance(execution_or_id, str):
            execution = self.prescription_repository.get_execution_by_id(execution_or_id)
            if not execution:
                execution = self.pill_pack_repository.get_execution_by_id(execution_or_id)
            if not execution:
                raise ValueError(f"Execução com ID {execution_or_id} não encontrada.")
        else:
            execution = execution_or_id

        if not execution.storage_image_path:
            raise ValueError("A execução informada não possui uma imagem associada.")

        if execution.execution_type == "prescription":
            return await self.prescription_repository.get_image(execution.id)
        elif execution.execution_type == "pillpack":
            return await self.pill_pack_repository.get_image(execution.id)
        else:
            raise ValueError(f"Tipo de execução desconhecido: {execution.execution_type}")