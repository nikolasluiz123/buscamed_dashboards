import json
from typing import List, Optional

from src.data.repositories import ExecutionRepository
from src.domain.entities import ExecutionFilter, ExecutionAnalyticsResult
from src.domain.use_cases.calculate_pill_pack_accuracy_use_case import CalculatePillPackAccuracyUseCase
from src.domain.ports.answer_key_provider import AnswerKeyProvider


class GetPillPacksAnalyticsUseCase:
    """
    Caso de uso responsável por compilar os dados de análise de desempenho de Cartelas de Comprimidos,
    filtrando apenas as execuções que possuem gabarito correspondente.
    """

    def __init__(
        self,
        repository: ExecutionRepository,
        accuracy_use_case: CalculatePillPackAccuracyUseCase,
        answer_key_provider: AnswerKeyProvider
    ):
        self._repository = repository
        self._accuracy_use_case = accuracy_use_case
        self._answer_key_provider = answer_key_provider

    def _extract_image_id(self, storage_path: str | None) -> str | None:
        """
        Extrai o identificador da imagem a partir do caminho do storage.
        """
        if not storage_path:
            return None
        return storage_path.replace("\\", "/").split("/")[-1].split(".")[0]

    def execute(self, filters: Optional[ExecutionFilter] = None) -> List[ExecutionAnalyticsResult]:
        """
        Executa a compilação dos dados de análise cruzando com os gabaritos disponíveis.

        Returns:
            List[ExecutionAnalyticsResult]: Lista de entidades contendo os dados analíticos processados.
        """
        executions = self._repository.get_all_executions(filters)
        if not executions:
            return []

        answer_keys = self._answer_key_provider.get_answer_keys()
        data_rows = []

        for execution in executions:
            expected_data = None
            if execution.storage_image_path:
                image_id = self._extract_image_id(execution.storage_image_path)
                expected_data = answer_keys.get(image_id)
            else:
                expected_data = answer_keys.get(execution.id)

            if not expected_data:
                continue

            processing_time = (execution.end_date - execution.start_date).total_seconds()
            accuracy = 0.0

            if execution.result:
                try:
                    predicted_data = json.loads(execution.result)
                    accuracy = self._accuracy_use_case._evaluate_pill_pack(expected_data, predicted_data) * 100
                except json.JSONDecodeError:
                    pass

            result_entity = ExecutionAnalyticsResult(
                execution_id=execution.id,
                start_date=execution.start_date,
                input_tokens=execution.input_tokens or 0,
                output_tokens=execution.output_tokens or 0,
                processing_time_seconds=processing_time,
                accuracy_percentage=accuracy
            )
            data_rows.append(result_entity)

        return data_rows