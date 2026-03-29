import json
from typing import List, Dict, Any

from src.data.repositories import ExecutionRepository
from src.domain.use_cases.calculate_pill_pack_accuracy_use_case import CalculatePillPackAccuracyUseCase


class GetPillPacksAnalyticsUseCase:
    """
    Caso de uso responsável por compilar os dados de análise de desempenho de Cartelas de Comprimidos,
    filtrando apenas as execuções que possuem gabarito correspondente.
    """

    def __init__(
        self,
        repository: ExecutionRepository,
        accuracy_use_case: CalculatePillPackAccuracyUseCase,
        answer_key_path: str
    ):
        self._repository = repository
        self._accuracy_use_case = accuracy_use_case
        self._answer_key_path = answer_key_path
        self._answer_keys = self._load_answer_keys()

    def _load_answer_keys(self) -> List[Dict[str, Any]]:
        """
        Carrega o JSON de gabarito para a memória.
        """
        try:
            with open(self._answer_key_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _extract_image_id(self, storage_path: str | None) -> str | None:
        """
        Extrai o identificador da imagem a partir do caminho do storage.
        """
        if not storage_path:
            return None
        return storage_path.replace("\\", "/").split("/")[-1].split(".")[0]

    def execute(self) -> List[Dict[str, Any]]:
        """
        Executa a compilação dos dados de análise cruzando com os gabaritos disponíveis.

        Returns:
            List[Dict[str, Any]]: Lista de dicionários contendo os dados formatados para análise.
        """
        executions = self._repository.get_all_executions()
        if not executions:
            return []

        data_rows = []
        for execution in executions:
            expected_data = None
            if execution.storage_image_path:
                image_id = self._extract_image_id(execution.storage_image_path)
                expected_data = next((item for item in self._answer_keys if item.get("id") == image_id), None)
            else:
                expected_data = next((item for item in self._answer_keys if item.get("id") == execution.id), None)

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

            data_rows.append({
                "Data": execution.start_date,
                "ID": execution.id,
                "Tokens de Entrada": execution.input_tokens or 0,
                "Tokens de Saída": execution.output_tokens or 0,
                "Tempo (s)": processing_time,
                "Acurácia": accuracy
            })

        return data_rows