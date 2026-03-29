import pandas as pd

from src.domain.use_cases.get_prescriptions_analytics_use_case import GetPrescriptionsAnalyticsUseCase


class PrescriptionsAnalyticsViewModel:
    """
    ViewModel responsável por consolidar os dados de análise de desempenho de Prescrições Médicas.
    """

    def __init__(self, analytics_use_case: GetPrescriptionsAnalyticsUseCase):
        self._analytics_use_case = analytics_use_case

    def get_performance_dataframe(self) -> pd.DataFrame:
        """
        Constrói e retorna um DataFrame do Pandas com os indicadores calculados de todas as execuções.
        """
        data = self._analytics_use_case.execute()
        df = pd.DataFrame(data)

        if df.empty:
            return df

        return df.sort_values(by="Data")