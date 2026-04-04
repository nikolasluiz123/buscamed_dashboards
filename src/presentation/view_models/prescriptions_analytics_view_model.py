import pandas as pd
from typing import List, Optional

from src.data.repositories import ExecutionRepository
from src.domain.entities import ExecutionFilter, ExecutionAnalyticsResult
from src.domain.use_cases.get_prescriptions_analytics_use_case import GetPrescriptionsAnalyticsUseCase


class PrescriptionsAnalyticsViewModel:

    def __init__(self, analytics_use_case: GetPrescriptionsAnalyticsUseCase, repository: ExecutionRepository):
        self._analytics_use_case = analytics_use_case
        self._repository = repository

    def get_available_prompts(self) -> List[str]:
        return self._repository.get_available_prompts()

    def _map_to_dataframe(self, results: List[ExecutionAnalyticsResult]) -> pd.DataFrame:
        mapped_data = [
            {
                "Data": result.start_date,
                "ID": result.execution_id,
                "Tokens de Entrada": result.input_tokens,
                "Tokens de Saída": result.output_tokens,
                "Tempo (s)": result.processing_time_seconds,
                "Acurácia": result.accuracy_percentage
            }
            for result in results
        ]
        return pd.DataFrame(mapped_data)

    def get_performance_dataframe(self, filters: Optional[ExecutionFilter] = None) -> pd.DataFrame:
        results = self._analytics_use_case.execute(filters)
        df = self._map_to_dataframe(results)

        if df.empty:
            return df

        return df.sort_values(by="Data")

    def get_available_client_processor_versions(self) -> List[str]:
        return self._repository.get_available_client_processor_versions()