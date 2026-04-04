import json
from typing import List, Optional

from src.data.repositories import ExecutionRepository, AnswerKeyRepository
from src.domain.entities import ExecutionFilter, EvaluatedExecution
from src.domain.use_cases.calculate_pill_pack_accuracy_use_case import CalculatePillPackAccuracyUseCase


class GetEvaluatedPillPacksUseCase:
    """
    Caso de uso responsável por recuperar as cartelas executadas, cruzar com
    os gabaritos do banco de dados e calcular a acurácia individual de cada uma.
    """

    def __init__(
            self,
            repository: ExecutionRepository,
            answer_key_repository: AnswerKeyRepository,
            accuracy_use_case: CalculatePillPackAccuracyUseCase
    ):
        self._repository = repository
        self._answer_key_repository = answer_key_repository
        self._accuracy_use_case = accuracy_use_case

    def execute(self, filters: Optional[ExecutionFilter] = None) -> List[EvaluatedExecution]:
        executions = self._repository.get_all_executions(filters)
        answer_keys = self._answer_key_repository.get_answer_keys(document_type="pillpack")
        answer_key_dict = {ak.execution_id: ak.content for ak in answer_keys}

        evaluated_list = []

        for ex in executions:
            expected_data = answer_key_dict.get(ex.id)

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