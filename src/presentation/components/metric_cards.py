from typing import List
import streamlit as st

from src.domain.entities import Execution
from src.domain.use_cases.evaluation.calculate_processing_time_use_case import CalculateProcessingTimeUseCase


def render_metrics(
        executions: List[Execution],
        accuracy: float,
        calc_time_use_case: CalculateProcessingTimeUseCase
) -> None:
    """
    Renderiza os cartões de métricas agregadas para um conjunto de execuções.

    Args:
        executions (List[Execution]): Lista de execuções para calcular as métricas.
        accuracy (float): O valor de acurácia global já calculado previamente.
        calc_time_use_case (CalculateProcessingTimeUseCase): Caso de uso para calcular o tempo de cada execução.
    """
    if not executions:
        st.info("Nenhum dado disponível para exibir métricas nesta aba.")
        return

    total_input_tokens = sum(e.input_tokens for e in executions if e.input_tokens is not None)
    total_output_tokens = sum(e.output_tokens for e in executions if e.output_tokens is not None)

    processing_times = [calc_time_use_case.execute(e) for e in executions]
    avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0.0

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(label="Total de Execuções", value=len(executions))

    with col2:
        st.metric(label="Acurácia do Gabarito", value=f"{accuracy:.2f}%")

    with col3:
        st.metric(label="Tempo Médio (s)", value=f"{avg_processing_time:.2f}s")

    with col4:
        st.metric(label="Tokens (Input / Output)", value=f"{total_input_tokens} / {total_output_tokens}")