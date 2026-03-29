import streamlit as st

from src.presentation.view_models.prescriptions_analytics_view_model import PrescriptionsAnalyticsViewModel
from src.presentation.components.analytics_charts import render_performance_charts


def render_prescriptions_analytics_page(view_model: PrescriptionsAnalyticsViewModel) -> None:
    """
    Renderiza a página de Análise de Desempenho para Prescrições Médicas.
    """
    st.title("Análise de Desempenho: Prescrições Médicas")
    st.write("Visão agregada do comportamento e custo da LLM ao longo das execuções.")

    df = view_model.get_performance_dataframe()
    render_performance_charts(df)