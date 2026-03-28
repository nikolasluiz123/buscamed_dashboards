from src.domain.entities import Execution


class CalculateProcessingTimeUseCase:
    """
    Caso de uso para calcular o tempo total de processamento de uma execução em segundos.
    """

    def execute(self, execution: Execution) -> float:
        if not execution.start_date or not execution.end_date:
            return 0.0

        delta = execution.end_date - execution.start_date
        return delta.total_seconds()