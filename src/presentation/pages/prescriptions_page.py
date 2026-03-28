import asyncio
import streamlit as st

from src.di.container import ApplicationContainer
from src.presentation.components.filters import render_execution_selector
from src.presentation.components.execution_details import render_execution_details
from src.presentation.components.metric_cards import render_metrics


def render_prescriptions_page(container: ApplicationContainer) -> None:
    """
    Renderiza a página principal de avaliação de Prescrições Médicas,
    dividindo a visualização entre processamento de imagem e texto.
    """
    st.title("Avaliação: Prescrições Médicas")

    repo = container.prescription_repository()
    sync_use_case = container.sync_prescription_executions_use_case()
    accuracy_use_case = container.calculate_prescription_accuracy_use_case()
    calc_time_use_case = container.calculate_processing_time_use_case()
    get_image_use_case = container.get_image_use_case()

    col_title, col_button = st.columns([8, 2])
    with col_button:
        if st.button("🔄 Sincronizar Dados", use_container_width=True):
            with st.spinner("Buscando novas execuções..."):
                new_records = asyncio.run(sync_use_case.execute())
                if new_records > 0:
                    st.success(f"{new_records} novos registros sincronizados!")
                else:
                    st.info("O banco de dados já está atualizado.")

    executions = repo.get_all_executions()

    image_executions = [e for e in executions if e.storage_image_path is not None]
    text_executions = [e for e in executions if e.storage_image_path is None]

    global_accuracy = accuracy_use_case.execute()

    tab_image, tab_text = st.tabs(["Processamento de Imagem", "Processamento de Texto"])

    with tab_image:
        render_metrics(image_executions, global_accuracy, calc_time_use_case)
        selected_img_execution = render_execution_selector(image_executions, "presc_img")

        if selected_img_execution:
            render_execution_details(selected_img_execution, get_image_use_case)

    with tab_text:
        render_metrics(text_executions, 0.0, calc_time_use_case)
        selected_txt_execution = render_execution_selector(text_executions, "presc_txt")

        if selected_txt_execution:
            render_execution_details(selected_txt_execution, get_image_use_case)