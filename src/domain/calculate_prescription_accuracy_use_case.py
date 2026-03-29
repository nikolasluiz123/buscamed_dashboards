import json
import os

from src.data.repositories import ExecutionRepository
from src.data.file.file_reader import FileReader
from src.domain.use_cases.evaluation.evaluate_single_prescription_use_case import EvaluateSinglePrescriptionUseCase


class CalculatePrescriptionAccuracyUseCase:
    """
    Calcula a acurácia média global das execuções de Receitas Médicas.
    """

    def __init__(
            self,
            repository: ExecutionRepository,
            file_reader: FileReader,
            answer_key_path: str,
            single_evaluator: EvaluateSinglePrescriptionUseCase
    ):
        self.repository = repository
        self.file_reader = file_reader
        self.answer_key_path = answer_key_path
        self.single_evaluator = single_evaluator

    def execute(self) -> float:
        """
        Calcula a média de acurácia de todas as execuções válidas no banco de dados.

        Returns:
            float: A acurácia média em porcentagem (0.0 a 100.0).
        """
        executions = self.repository.get_all_executions()
        answer_key_data = self.file_reader.load_json(self.answer_key_path)

        total_score = 0.0
        valid_executions = 0

        for execution in executions:
            if not execution.result:
                continue

            if execution.storage_image_path:
                execution_id = self._extract_id_from_path(execution.storage_image_path)
            else:
                execution_id = execution.id

            if execution_id not in answer_key_data:
                continue

            try:
                predicted_json = json.loads(execution.result)
                expected_json = answer_key_data[execution_id]

                execution_score = self.single_evaluator.execute(expected_json, predicted_json)
                total_score += execution_score
                valid_executions += 1

            except json.JSONDecodeError:
                continue

        return (total_score / valid_executions * 100) if valid_executions > 0 else 0.0

    def _extract_id_from_path(self, storage_image_path: str) -> str:
        """
        Extrai o identificador do arquivo a partir do caminho completo do storage.
        """
        file_name = os.path.basename(storage_image_path)
        return os.path.splitext(file_name)[0]