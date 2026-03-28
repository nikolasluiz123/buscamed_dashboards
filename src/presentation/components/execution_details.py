import json
import asyncio
import streamlit as st

from src.domain.entities import Execution
from src.domain.use_cases.get_image_use_case import GetImageUseCase


def render_execution_details(execution: Execution, get_image_use_case: GetImageUseCase) -> None:
    """
    Renderiza os detalhes de uma execução contendo o JSON de resultado e a imagem processada.

    Args:
        execution (Execution): A execução que será detalhada.
        get_image_use_case (GetImageUseCase): Caso de uso para obter os bytes da imagem de forma assíncrona.
    """
    st.divider()
    st.subheader(f"Detalhes da Execução", anchor=False)

    col_text, col_img = st.columns([1, 1])

    with col_text:
        st.markdown("#### Resultado (JSON)")
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
            st.info("Esta execução não possui imagem associada (Processamento exclusivo de texto).")