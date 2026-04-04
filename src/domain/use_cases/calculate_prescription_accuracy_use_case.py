import json
from typing import Optional

from src.data.repositories import ExecutionRepository, AnswerKeyRepository
from src.domain.use_cases.evaluation.evaluate_single_prescription_use_case import EvaluateSinglePrescriptionUseCase
from src.domain.entities import ExecutionFilter


class CalculatePrescriptionAccuracyUseCase:
    """
    Calcula a acurácia média global das execuções de Receitas Médicas utilizando a base de gabaritos.
    """

    def __init__(
            self,
            repository: ExecutionRepository,
            answer_key_repository: AnswerKeyRepository,
            single_evaluator: EvaluateSinglePrescriptionUseCase
    ):
        self.repository = repository
        self.answer_key_repository = answer_key_repository
        self.single_evaluator = single_evaluator

    def execute(self, filters: Optional[ExecutionFilter] = None) -> float:
        """
        Calcula a média de acurácia de todas as execuções válidas no banco de dados.
        """
        executions = self.repository.get_all_executions(filters)
        answer_keys = self.answer_key_repository.get_answer_keys(document_type="prescription")
        answer_key_dict = {ak.execution_id: ak.content for ak in answer_keys}

        total_score = 0.0
        valid_executions = 0

        for execution in executions:
            if not execution.result:
                continue

            if execution.id not in answer_key_dict:
                continue

            try:
                predicted_json = json.loads(execution.result)
                expected_json = answer_key_dict[execution.id]

                execution_score = self.single_evaluator.execute(expected_json, predicted_json)
                total_score += execution_score
                valid_executions += 1

            except json.JSONDecodeError:
                continue

        return (total_score / valid_executions * 100) if valid_executions > 0 else 0.0