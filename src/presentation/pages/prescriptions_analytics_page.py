import streamlit as st

from src.domain.entities import ExecutionFilter
from src.presentation.view_models.prescriptions_analytics_view_model import PrescriptionsAnalyticsViewModel
from src.presentation.components.analytics_charts import render_performance_charts


def render_prescriptions_analytics_page(view_model: PrescriptionsAnalyticsViewModel) -> None:
    """
    Renderiza a página de Análise de Desempenho para Prescrições Médicas.
    """
    st.title("Análise de Desempenho: Prescrições Médicas")
    st.write("Visão agregada do comportamento e custo da LLM ao longo das execuções.")

    st.divider()

    available_prompts = view_model.get_available_prompts()
    selected_prompt = st.selectbox(
        "Filtrar por Versão do Prompt:",
        options=["Todos"] + available_prompts,
        key="prescriptions_analytics_prompt_filter"
    )

    prompt_filter = None if selected_prompt == "Todos" else selected_prompt
    execution_filter = ExecutionFilter(prompt=prompt_filter)

    df = view_model.get_performance_dataframe(filters=execution_filter)

    if df.empty:
        st.info("Nenhuma execução encontrada para o filtro selecionado.")
    else:
        render_performance_charts(df)