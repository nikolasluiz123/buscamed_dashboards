import streamlit as st

from src.presentation.view_models.pill_packs_analytics_view_model import PillPacksAnalyticsViewModel
from src.presentation.components.analytics_charts import render_performance_charts


def render_pill_packs_analytics_page(view_model: PillPacksAnalyticsViewModel) -> None:
    """
    Renderiza a página de Análise de Desempenho para Cartelas de Comprimidos.
    """
    st.title("Análise de Desempenho: Cartelas de Comprimidos")
    st.write("Visão agregada do comportamento e custo da LLM ao longo das execuções.")

    df = view_model.get_performance_dataframe()
    render_performance_charts(df)