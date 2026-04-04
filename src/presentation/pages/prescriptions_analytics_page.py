import streamlit as st

from src.domain.entities import ExecutionFilter, ExecutionType
from src.presentation.view_models.prescriptions_analytics_view_model import PrescriptionsAnalyticsViewModel
from src.presentation.components.analytics_charts import render_performance_charts
from src.presentation.components.filters import render_client_processor_version_filter, render_llm_model_filter


def render_prescriptions_analytics_page(view_model: PrescriptionsAnalyticsViewModel) -> None:
    """
    Renderiza a página de Análise de Desempenho para Prescrições Médicas.
    """
    st.title("Análise de Desempenho: Prescrições Médicas")
    st.write("Visão agregada do comportamento e custo da LLM ao longo das execuções.")

    st.divider()

    col_prompt, col_version, col_type, col_model = st.columns(4)

    available_prompts = view_model.get_available_prompts()
    with col_prompt:
        selected_prompt = st.selectbox(
            "Filtrar por Versão do Prompt:",
            options=["Todos"] + available_prompts,
            key="prescriptions_analytics_prompt_filter"
        )

    available_versions = view_model.get_available_client_processor_versions()
    with col_version:
        selected_version = render_client_processor_version_filter(
            available_versions,
            key_prefix="prescriptions_analytics"
        )

    with col_type:
        selected_type = st.selectbox(
            "Filtrar por Tipo de Processamento:",
            options=["Todos", "Imagem", "Texto"],
            key="prescriptions_analytics_type_filter"
        )

    available_models = view_model.get_available_llm_models()
    with col_model:
        selected_model = render_llm_model_filter(
            available_models,
            key_prefix="prescriptions_analytics"
        )

    prompt_filter = None if selected_prompt == "Todos" else selected_prompt
    type_filter = None
    if selected_type == "Imagem":
        type_filter = ExecutionType.IMAGE
    elif selected_type == "Texto":
        type_filter = ExecutionType.TEXT

    execution_filter = ExecutionFilter(
        prompt=prompt_filter,
        processing_type=type_filter,
        client_processor_version=selected_version,
        llm_model=selected_model
    )

    df = view_model.get_performance_dataframe(filters=execution_filter)

    if df.empty:
        st.info("Nenhuma execução encontrada para o filtro selecionado.")
    else:
        render_performance_charts(df)