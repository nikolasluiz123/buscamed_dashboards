import json
from typing import List, Optional

from src.data.repositories import ExecutionRepository, AnswerKeyRepository
from src.domain.use_cases.evaluation.evaluate_single_prescription_use_case import EvaluateSinglePrescriptionUseCase
from src.domain.entities import ExecutionFilter, ExecutionAnalyticsResult


class GetPrescriptionsAnalyticsUseCase:
    """
    Caso de uso responsável por compilar os dados de análise de desempenho de Prescrições Médicas,
    filtrando apenas as execuções que possuem gabarito correspondente no banco.
    """

    def __init__(
            self,
            repository: ExecutionRepository,
            single_accuracy_use_case: EvaluateSinglePrescriptionUseCase,
            answer_key_repository: AnswerKeyRepository
    ):
        self._repository = repository
        self._single_accuracy_use_case = single_accuracy_use_case
        self._answer_key_repository = answer_key_repository

    def execute(self, filters: Optional[ExecutionFilter] = None) -> List[ExecutionAnalyticsResult]:
        """
        Executa a compilação dos dados de análise cruzando com os gabaritos disponíveis.
        """
        executions = self._repository.get_all_executions(filters)
        if not executions:
            return []

        answer_keys = self._answer_key_repository.get_answer_keys(document_type="prescription")
        answer_key_dict = {ak.execution_id: ak.content for ak in answer_keys}

        data_rows = []

        for execution in executions:
            expected_data = answer_key_dict.get(execution.id)

            if not expected_data:
                continue

            processing_time = (execution.end_date - execution.start_date).total_seconds()
            accuracy = 0.0

            if execution.result:
                try:
                    predicted_data = json.loads(execution.result)
                    accuracy = self._single_accuracy_use_case.execute(expected_data, predicted_data) * 100
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