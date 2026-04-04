import asyncio
import copy
from typing import List, Optional

from src.domain.entities import ExecutionFilter, EvaluatedExecution, ExecutionType
from src.data.repositories import ExecutionRepository
from src.domain.use_cases.sync_executions_use_case import SyncExecutionsUseCase
from src.domain.calculate_prescription_accuracy_use_case import CalculatePrescriptionAccuracyUseCase
from src.domain.use_cases.evaluation.calculate_processing_time_use_case import CalculateProcessingTimeUseCase
from src.domain.use_cases.get_image_use_case import GetImageUseCase
from src.domain.use_cases.get_evaluated_prescriptions_use_case import GetEvaluatedPrescriptionsUseCase

class PrescriptionsViewModel:
    def __init__(
        self,
        repository: ExecutionRepository,
        sync_use_case: SyncExecutionsUseCase,
        accuracy_use_case: CalculatePrescriptionAccuracyUseCase,
        calc_time_use_case: CalculateProcessingTimeUseCase,
        get_image_use_case: GetImageUseCase,
        get_evaluated_use_case: GetEvaluatedPrescriptionsUseCase
    ):
        self._repository = repository
        self._sync_use_case = sync_use_case
        self._accuracy_use_case = accuracy_use_case
        self.calc_time_use_case = calc_time_use_case
        self.get_image_use_case = get_image_use_case
        self._get_evaluated_use_case = get_evaluated_use_case

    def sync_data(self) -> int:
        return asyncio.run(self._sync_use_case.execute())

    def get_available_prompts(self) -> List[str]:
        return self._repository.get_available_prompts()

    def get_global_accuracy(self, filters: Optional[ExecutionFilter] = None) -> float:
        return self._accuracy_use_case.execute(filters)

    def get_evaluated_image_executions(self, filters: Optional[ExecutionFilter] = None) -> List[EvaluatedExecution]:
        img_filter = copy.copy(filters) if filters else ExecutionFilter()
        img_filter.processing_type = ExecutionType.IMAGE
        return self._get_evaluated_use_case.execute(img_filter)

    def get_evaluated_text_executions(self, filters: Optional[ExecutionFilter] = None) -> List[EvaluatedExecution]:
        txt_filter = copy.copy(filters) if filters else ExecutionFilter()
        txt_filter.processing_type = ExecutionType.TEXT
        return self._get_evaluated_use_case.execute(txt_filter)

    def get_available_client_processor_versions(self) -> List[str]:
        return self._repository.get_available_client_processor_versions()