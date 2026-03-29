import json
from typing import List, Optional

from src.data.repositories import ExecutionRepository
from src.domain.entities import ExecutionFilter, EvaluatedExecution
from src.domain.ports.answer_key_provider import AnswerKeyProvider
from src.domain.use_cases.calculate_pill_pack_accuracy_use_case import CalculatePillPackAccuracyUseCase

class GetEvaluatedPillPacksUseCase:
    """
    Caso de uso responsável por recuperar as cartelas executadas, cruzar com
    os gabaritos disponíveis e calcular a acurácia individual de cada uma.
    """

    def __init__(
        self,
        repository: ExecutionRepository,
        answer_key_provider: AnswerKeyProvider,
        accuracy_use_case: CalculatePillPackAccuracyUseCase
    ):
        self._repository = repository
        self._answer_key_provider = answer_key_provider
        self._accuracy_use_case = accuracy_use_case

    def _extract_image_id(self, storage_path: str | None) -> str | None:
        if not storage_path:
            return None
        return storage_path.replace("\\", "/").split("/")[-1].split(".")[0]

    def execute(self, filters: Optional[ExecutionFilter] = None, require_image: bool = True) -> List[EvaluatedExecution]:
        executions = self._repository.get_all_executions(filters)
        answer_keys = self._answer_key_provider.get_answer_keys()
        evaluated_list = []

        for ex in executions:
            if require_image and not ex.storage_image_path:
                continue
            if not require_image and ex.storage_image_path:
                continue

            expected_data = None
            if ex.storage_image_path:
                image_id = self._extract_image_id(ex.storage_image_path)
                expected_data = answer_keys.get(image_id)
            else:
                expected_data = answer_keys.get(ex.id)

            if not expected_data:
                continue

            accuracy = 0.0
            if ex.result:
                try:
                    predicted_data = json.loads(ex.result)
                    accuracy = self._accuracy_use_case._evaluate_pill_pack(expected_data, predicted_data) * 100
                except json.JSONDecodeError:
                    pass

            evaluated_list.append(
                EvaluatedExecution(
                    execution=ex,
                    expected_data=expected_data,
                    accuracy_score=accuracy
                )
            )

        return evaluated_list