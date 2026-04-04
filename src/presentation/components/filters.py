from typing import List, Optional
import streamlit as st
from src.domain.entities import Execution

def render_execution_selector(executions: List[Execution], key_prefix: str) -> Optional[Execution]:
    """
    Renderiza um selectbox para seleção de uma execução específica.

    Args:
        executions (List[Execution]): Lista de execuções disponíveis para seleção.
        key_prefix (str): Prefixo único para garantir que o componente no Streamlit não tenha conflito de chaves de estado.

    Returns:
        Optional[Execution]: A execução selecionada ou None se a lista for vazia.
    """
    if not executions:
        return None

    options = {
        execution.id: f"{execution.start_date.strftime('%d/%m/%Y %H:%M:%S')} - ID: {execution.id}"
        for execution in executions
    }

    selected_id = st.selectbox(
        "Selecione uma execução para visualização detalhada:",
        options=list(options.keys()),
        format_func=lambda execution_id: options[execution_id],
        key=f"selectbox_execution_{key_prefix}"
    )

    for execution in executions:
        if execution.id == selected_id:
            return execution

    return None


def render_client_processor_version_filter(available_versions: List[str], key_prefix: str) -> Optional[str]:
    """
    Renderiza um selectbox para filtragem por versão do client processor.

    Args:
        available_versions (List[str]): Lista de versões disponíveis no banco de dados.
        key_prefix (str): Prefixo único para o controle de estado no Streamlit.

    Returns:
        Optional[str]: A versão selecionada para filtro ou None se 'Todas' for selecionado.
    """
    options = ["Todas"] + (available_versions if available_versions else [])

    selected_version = st.selectbox(
        "Filtrar por Versão do Client Processor:",
        options=options,
        key=f"selectbox_client_processor_version_{key_prefix}"
    )

    if selected_version == "Todas":
        return None

    return selected_version