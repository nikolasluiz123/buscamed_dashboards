import pandas as pd
from typing import List, Optional

from src.data.repositories import ExecutionRepository
from src.domain.entities import ExecutionFilter
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

    def get_performance_dataframe(self, filters: Optional[ExecutionFilter] = None) -> pd.DataFrame:
        """
        Constrói e retorna um DataFrame do Pandas com os indicadores calculados de todas as execuções.
        """
        data = self._analytics_use_case.execute(filters)
        df = pd.DataFrame(data)

        if df.empty:
            return df

        return df.sort_values(by="Data")