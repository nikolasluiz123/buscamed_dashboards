# src/presentation/view_models/prescriptions_view_model.py
import json
from typing import List, Optional, Dict, Any

from src.domain.entities import Execution, ExecutionFilter
from src.data.repositories import ExecutionRepository
from src.domain.use_cases.sync_executions_use_case import SyncExecutionsUseCase
from src.domain.calculate_prescription_accuracy_use_case import CalculatePrescriptionAccuracyUseCase
from src.domain.use_cases.evaluation.calculate_processing_time_use_case import CalculateProcessingTimeUseCase
from src.domain.use_cases.get_image_use_case import GetImageUseCase
from src.domain.use_cases.evaluation.evaluate_single_prescription_use_case import EvaluateSinglePrescriptionUseCase


class PrescriptionsViewModel:
    """
    ViewModel responsável por preparar e abstrair os dados de Prescrições Médicas para a interface de usuário.
    """

    def __init__(
        self,
        repository: ExecutionRepository,
        sync_use_case: SyncExecutionsUseCase,
        accuracy_use_case: CalculatePrescriptionAccuracyUseCase,
        calc_time_use_case: CalculateProcessingTimeUseCase,
        get_image_use_case: GetImageUseCase,
        single_accuracy_use_case: EvaluateSinglePrescriptionUseCase,
        answer_key_path: str
    ):
        self._repository = repository
        self._sync_use_case = sync_use_case
        self._accuracy_use_case = accuracy_use_case
        self.calc_time_use_case = calc_time_use_case
        self.get_image_use_case = get_image_use_case
        self._single_accuracy_use_case = single_accuracy_use_case
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

    async def sync_data(self) -> int:
        """
        Sincroniza os dados com a API remota.
        """
        return await self._sync_use_case.execute()

    def get_available_prompts(self) -> List[str]:
        """
        Retorna a lista de prompts únicos disponíveis no banco de dados para Prescrições.
        """
        return self._repository.get_available_prompts()


    def get_global_accuracy(self, filters: Optional[ExecutionFilter] = None) -> float:
        """
        Calcula e retorna a acurácia global das execuções.
        """
        return self._accuracy_use_case.execute(filters)

    def get_image_executions(self, filters: Optional[ExecutionFilter] = None) -> List[Execution]:
        """
        Retorna as execuções que possuem processamento de imagem e que constam no gabarito.
        """
        executions = [e for e in self._repository.get_all_executions(filters) if e.storage_image_path is not None]
        return [e for e in executions if self.get_expected_data_for_image(e) is not None]

    def get_text_executions(self, filters: Optional[ExecutionFilter] = None) -> List[Execution]:
        """
        Retorna as execuções restritas apenas ao processamento de texto e que constam no gabarito.
        """
        executions = [e for e in self._repository.get_all_executions(filters) if e.storage_image_path is None]
        return [e for e in executions if self.get_expected_data_for_text(e) is not None]

    def _extract_image_id(self, storage_path: str | None) -> str | None:
        """
        Extrai o identificador da imagem a partir do caminho do storage.
        """
        if not storage_path:
            return None
        file_name = storage_path.replace("\\", "/").split("/")[-1]
        return file_name.split(".")[0]

    def get_expected_data_for_image(self, execution: Execution) -> Optional[Dict[str, Any]]:
        """
        Recupera os dados esperados (gabarito) associados a uma execução de imagem.
        """
        image_id = self._extract_image_id(execution.storage_image_path)
        return next((item for item in self._answer_keys if item.get("id") == image_id), None)

    def get_expected_data_for_text(self, execution: Execution) -> Optional[Dict[str, Any]]:
        """
        Recupera os dados esperados (gabarito) associados a uma execução de texto.
        """
        return next((item for item in self._answer_keys if item.get("id") == execution.id), None)

    def calculate_individual_accuracy(self, expected_data: Optional[Dict[str, Any]], result_str: Optional[str]) -> Optional[float]:
        """
        Realiza o parse do JSON da LLM e calcula a similaridade da execução com o gabarito.
        """
        if not expected_data or not result_str:
            return None
        try:
            predicted_data = json.loads(result_str)
            return self._single_accuracy_use_case.execute(expected_data, predicted_data) * 100
        except json.JSONDecodeError:
            return None