import json
import asyncio
import streamlit as st

from src.di.container import ApplicationContainer
from src.presentation.components.filters import render_execution_selector
from src.presentation.components.execution_details import render_execution_details
from src.presentation.components.metric_cards import render_metrics


def _extract_image_id(storage_path: str | None) -> str | None:
    """
    Extrai o identificador da imagem a partir do caminho do storage.

    Args:
        storage_path (str | None): O caminho completo da imagem no storage.

    Returns:
        str | None: O identificador extraído ou None se o caminho for inválido.
    """
    if not storage_path:
        return None

    file_name = storage_path.replace("\\", "/").split("/")[-1]
    base_name = file_name.split(".")[0]
    return base_name


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
    single_accuracy_use_case = container.evaluate_single_prescription_use_case()

    try:
        with open(container.config.prescription_answer_key_path(), "r", encoding="utf-8") as f:
            answer_keys = json.load(f)
    except Exception:
        answer_keys = []

    col_title, col_button = st.columns([8, 2])
    with col_button:
        if st.button("🔄 Sincronizar Dados", width="stretch"):
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
            image_id = _extract_image_id(selected_img_execution.storage_image_path)
            expected_data = next((item for item in answer_keys if item.get("id") == image_id), None)

            individual_score = None
            if expected_data and selected_img_execution.result:
                try:
                    predicted_data = json.loads(selected_img_execution.result)
                    individual_score = single_accuracy_use_case.execute(expected_data, predicted_data) * 100
                except json.JSONDecodeError:
                    pass

            render_execution_details(
                execution=selected_img_execution,
                get_image_use_case=get_image_use_case,
                expected_json=expected_data,
                individual_accuracy=individual_score
            )

    with tab_text:
        render_metrics(text_executions, 0.0, calc_time_use_case)
        selected_txt_execution = render_execution_selector(text_executions, "presc_txt")

        if selected_txt_execution:
            expected_data = next((item for item in answer_keys if item.get("id") == selected_txt_execution.id), None)

            individual_score = None
            if expected_data and selected_txt_execution.result:
                try:
                    predicted_data = json.loads(selected_txt_execution.result)
                    individual_score = single_accuracy_use_case.execute(expected_data, predicted_data) * 100
                except json.JSONDecodeError:
                    pass

            render_execution_details(
                execution=selected_txt_execution,
                get_image_use_case=get_image_use_case,
                expected_json=expected_data,
                individual_accuracy=individual_score
            )