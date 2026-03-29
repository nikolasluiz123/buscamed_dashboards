import asyncio
import streamlit as st

from src.presentation.view_models.prescriptions_view_model import PrescriptionsViewModel
from src.presentation.components.filters import render_execution_selector
from src.presentation.components.execution_details import render_execution_details
from src.presentation.components.metric_cards import render_metrics


def render_prescriptions_page(view_model: PrescriptionsViewModel) -> None:
    """
    Renderiza a página principal de avaliação de Prescrições Médicas,
    dividindo a visualização entre processamento de imagem e texto.
    """
    st.title("Avaliação: Prescrições Médicas")

    col_title, col_button = st.columns([8, 2])
    with col_button:
        if st.button("🔄 Sincronizar Dados", width="stretch"):
            with st.spinner("Buscando novas execuções..."):
                new_records = asyncio.run(view_model.sync_data())
                if new_records > 0:
                    st.success(f"{new_records} novos registros sincronizados!")
                else:
                    st.info("O banco de dados já está atualizado.")

    global_accuracy = view_model.get_global_accuracy()
    image_executions = view_model.get_image_executions()
    text_executions = view_model.get_text_executions()

    tab_image, tab_text = st.tabs(["Processamento de Imagem", "Processamento de Texto"])

    with tab_image:
        render_metrics(image_executions, global_accuracy, view_model.calc_time_use_case)
        selected_img_execution = render_execution_selector(image_executions, "presc_img")

        if selected_img_execution:
            expected_data = view_model.get_expected_data_for_image(selected_img_execution)
            individual_score = view_model.calculate_individual_accuracy(expected_data, selected_img_execution.result)

            render_execution_details(
                execution=selected_img_execution,
                get_image_use_case=view_model.get_image_use_case,
                expected_json=expected_data,
                individual_accuracy=individual_score
            )

    with tab_text:
        render_metrics(text_executions, 0.0, view_model.calc_time_use_case)
        selected_txt_execution = render_execution_selector(text_executions, "presc_txt")

        if selected_txt_execution:
            expected_data = view_model.get_expected_data_for_text(selected_txt_execution)
            individual_score = view_model.calculate_individual_accuracy(expected_data, selected_txt_execution.result)

            render_execution_details(
                execution=selected_txt_execution,
                get_image_use_case=view_model.get_image_use_case,
                expected_json=expected_data,
                individual_accuracy=individual_score
            )