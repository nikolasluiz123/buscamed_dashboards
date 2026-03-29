import asyncio
import json
from typing import List, Optional, Dict, Any

from src.domain.entities import Execution, ExecutionFilter, EvaluatedExecution
from src.data.repositories import ExecutionRepository
from src.domain.use_cases.get_evaluated_pill_packs_use_case import GetEvaluatedPillPacksUseCase
from src.domain.use_cases.sync_executions_use_case import SyncExecutionsUseCase
from src.domain.use_cases.calculate_pill_pack_accuracy_use_case import CalculatePillPackAccuracyUseCase
from src.domain.use_cases.evaluation.calculate_processing_time_use_case import CalculateProcessingTimeUseCase
from src.domain.use_cases.get_image_use_case import GetImageUseCase


class PillPacksViewModel:
    def __init__(
        self,
        repository: ExecutionRepository,
        sync_use_case: SyncExecutionsUseCase,
        accuracy_use_case: CalculatePillPackAccuracyUseCase,
        calc_time_use_case: CalculateProcessingTimeUseCase,
        get_image_use_case: GetImageUseCase,
        get_evaluated_use_case: GetEvaluatedPillPacksUseCase
    ):
        self._repository = repository
        self._sync_use_case = sync_use_case
        self._accuracy_use_case = accuracy_use_case
        self.calc_time_use_case = calc_time_use_case
        self.get_image_use_case = get_image_use_case
        self._get_evaluated_use_case = get_evaluated_use_case

    async def sync_data(self) -> int:
        return asyncio.run(self._sync_use_case.execute())

    def get_available_prompts(self) -> List[str]:
        return self._repository.get_available_prompts()

    def get_global_accuracy(self, filters: Optional[ExecutionFilter] = None) -> float:
        return self._accuracy_use_case.execute(filters)

    def get_evaluated_image_executions(self, filters: Optional[ExecutionFilter] = None) -> List[EvaluatedExecution]:
        return self._get_evaluated_use_case.execute(filters, require_image=True)

    def get_evaluated_text_executions(self, filters: Optional[ExecutionFilter] = None) -> List[EvaluatedExecution]:
        return self._get_evaluated_use_case.execute(filters, require_image=False)