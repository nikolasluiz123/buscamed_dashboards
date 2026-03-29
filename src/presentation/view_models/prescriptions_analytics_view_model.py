import pandas as pd
from typing import List, Optional

from src.data.repositories import ExecutionRepository
from src.domain.entities import ExecutionFilter, ExecutionAnalyticsResult
from src.domain.use_cases.get_prescriptions_analytics_use_case import GetPrescriptionsAnalyticsUseCase


class PrescriptionsAnalyticsViewModel:
    """
    ViewModel responsável por consolidar os dados de análise de desempenho de Prescrições Médicas.
    """

    def __init__(self, analytics_use_case: GetPrescriptionsAnalyticsUseCase, repository: ExecutionRepository):
        self._analytics_use_case = analytics_use_case
        self._repository = repository

    def get_available_prompts(self) -> List[str]:
        """
        Retorna a lista de prompts únicos disponíveis no banco de dados para Prescrições.
        """
        return self._repository.get_available_prompts()

    def _map_to_dataframe(self, results: List[ExecutionAnalyticsResult]) -> pd.DataFrame:
        """
        Mapeia a lista de entidades de domínio para o formato de exibição em DataFrame.
        """
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
        """
        Constrói e retorna um DataFrame do Pandas com os indicadores calculados de todas as execuções.
        """
        results = self._analytics_use_case.execute(filters)
        df = self._map_to_dataframe(results)

        if df.empty:
            return df

        return df.sort_values(by="Data")