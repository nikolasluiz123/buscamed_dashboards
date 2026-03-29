import streamlit as st

from src.domain.entities import ExecutionFilter
from src.presentation.view_models.prescriptions_view_model import PrescriptionsViewModel
from src.presentation.components.filters import render_execution_selector
from src.presentation.components.execution_details import render_execution_details
from src.presentation.components.metric_cards import render_metrics


def render_prescriptions_page(view_model: PrescriptionsViewModel) -> None:
    st.title("Avaliação: Prescrições Médicas")

    col_title, col_button = st.columns([8, 2])
    with col_button:
        if st.button("🔄 Sincronizar Dados", width="stretch"):
            with st.spinner("Buscando novas execuções..."):
                new_records = view_model.sync_data()
                if new_records > 0:
                    st.success(f"{new_records} novos registros sincronizados!")
                else:
                    st.info("O banco de dados já está atualizado.")

    st.divider()

    available_prompts = view_model.get_available_prompts()
    selected_prompt = st.selectbox(
        "Filtrar por Versão do Prompt:",
        options=["Todos"] + available_prompts
    )

    prompt_filter = None if selected_prompt == "Todos" else selected_prompt
    execution_filter = ExecutionFilter(prompt=prompt_filter)

    global_accuracy = view_model.get_global_accuracy(execution_filter)

    evaluated_image_execs = view_model.get_evaluated_image_executions(execution_filter)
    evaluated_text_execs = view_model.get_evaluated_text_executions(execution_filter)

    image_executions = [e.execution for e in evaluated_image_execs]
    text_executions = [e.execution for e in evaluated_text_execs]

    tab_image, tab_text = st.tabs(["Processamento de Imagem", "Processamento de Texto"])

    with tab_image:
        render_metrics(image_executions, global_accuracy, view_model.calc_time_use_case)
        selected_img_execution = render_execution_selector(image_executions, "presc_img")

        if selected_img_execution:
            evaluated = next(e for e in evaluated_image_execs if e.execution.id == selected_img_execution.id)

            render_execution_details(
                execution=evaluated.execution,
                get_image_use_case=view_model.get_image_use_case,
                expected_json=evaluated.expected_data,
                individual_accuracy=evaluated.accuracy_score
            )

    with tab_text:
        render_metrics(text_executions, 0.0, view_model.calc_time_use_case)
        selected_txt_execution = render_execution_selector(text_executions, "presc_txt")

        if selected_txt_execution:
            evaluated = next(e for e in evaluated_text_execs if e.execution.id == selected_txt_execution.id)
            render_execution_details(
                execution=evaluated.execution,
                get_image_use_case=view_model.get_image_use_case,
                expected_json=evaluated.expected_data,
                individual_accuracy=evaluated.accuracy_score
            )