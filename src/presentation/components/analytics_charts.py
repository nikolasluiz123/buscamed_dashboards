import pandas as pd
import streamlit as st


def render_performance_charts(df: pd.DataFrame) -> None:
    """
    Renderiza os gráficos de análise de desempenho a partir de um DataFrame.

    Args:
        df (pd.DataFrame): DataFrame contendo as colunas 'Data', 'Tokens de Entrada',
                           'Tokens de Saída', 'Acurácia' e 'Tempo (s)'.
    """
    if df.empty:
        st.info("Não há dados suficientes para exibir as análises.")
        return

    st.markdown("### Gasto de Tokens por Execução")
    st.bar_chart(
        data=df,
        x="Data",
        y=["Tokens de Entrada", "Tokens de Saída"],
        color=["#29b5e8", "#11567f"],
        width="stretch"
    )

    st.divider()

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### Acurácia por Execução (%)")
        st.line_chart(
            data=df,
            x="Data",
            y="Acurácia",
            color="#28a745",
            width="stretch"
        )

    with col2:
        st.markdown("### Tempo de Processamento (s)")
        st.area_chart(
            data=df,
            x="Data",
            y="Tempo (s)",
            color="#ffc107",
            width="stretch"
        )