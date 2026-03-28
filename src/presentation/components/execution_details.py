import json
import asyncio
import streamlit as st

from src.domain.entities import Execution
from src.domain.use_cases.get_image_use_case import GetImageUseCase


def render_execution_details(
    execution: Execution,
    get_image_use_case: GetImageUseCase,
    expected_json: dict | list | None = None,
    individual_accuracy: float | None = None
) -> None:
    """
    Renderiza os detalhes de uma execução contendo o gabarito, o JSON de resultado e a imagem processada,
    além de apresentar as métricas individuais da execução.

    Args:
        execution (Execution): A execução que será detalhada.
        get_image_use_case (GetImageUseCase): Caso de uso para obter os bytes da imagem de forma assíncrona.
        expected_json (dict | list | None): O JSON de gabarito esperado para comparação.
        individual_accuracy (float | None): Acurácia calculada especificamente para esta execução.
    """
    st.divider()
    st.subheader("Detalhes da Execução", anchor=False)

    processing_time = (execution.end_date - execution.start_date).total_seconds()

    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    with metric_col1:
        accuracy_text = f"{individual_accuracy:.1f}%" if individual_accuracy is not None else "N/A"
        st.metric("Acurácia (Específica)", accuracy_text)
    with metric_col2:
        st.metric("Tempo de Resposta", f"{processing_time:.2f}s")
    with metric_col3:
        st.metric("Tokens de Entrada", execution.input_tokens)
    with metric_col4:
        st.metric("Tokens de Saída", execution.output_tokens)

    st.markdown("<br>", unsafe_allow_html=True)

    col_expected, col_result, col_img = st.columns([2, 2, 1])

    with col_expected:
        st.markdown("#### Gabarito Esperado")
        if expected_json:
            st.json(expected_json)
        else:
            st.info("Gabarito não encontrado para esta execução.")

    with col_result:
        st.markdown("#### Retorno da LLM")
        if execution.result:
            try:
                parsed_json = json.loads(execution.result)
                st.json(parsed_json)
            except json.JSONDecodeError:
                st.code(execution.result, language="json")
        else:
            st.warning("A LLM não retornou nenhum resultado nesta execução.")

    with col_img:
        st.markdown("#### Arquivo Original")
        if execution.storage_image_path:
            with st.spinner("Carregando imagem..."):
                try:
                    image_bytes = asyncio.run(get_image_use_case.execute(execution))
                    st.image(image_bytes, use_container_width=True)
                except Exception as e:
                    st.error(f"Não foi possível carregar a imagem original.\n\nDetalhe do Erro: {str(e)}")
        else:
            st.info("Esta execução não possui imagem associada.")