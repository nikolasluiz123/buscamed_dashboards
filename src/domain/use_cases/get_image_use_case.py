from src.data.repositories import ExecutionRepository
from src.domain.entities import Execution


class GetImageUseCase:
    """
    Caso de uso para obter os bytes de uma imagem a partir de uma execução.
    """

    def __init__(self, prescription_repository: ExecutionRepository, pill_pack_repository: ExecutionRepository):
        self.prescription_repository = prescription_repository
        self.pill_pack_repository = pill_pack_repository

    async def execute(self, execution: Execution) -> bytes:
        if not execution.storage_image_path:
            raise ValueError("A execução informada não possui uma imagem associada.")

        if execution.execution_type == "prescription":
            return await self.prescription_repository.get_image(execution.id)
        elif execution.execution_type == "pillpack":
            return await self.pill_pack_repository.get_image(execution.id)
        else:
            raise ValueError(f"Tipo de execução desconhecido: {execution.execution_type}")