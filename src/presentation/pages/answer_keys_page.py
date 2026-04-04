import json
import asyncio
import streamlit as st
import pandas as pd
from src.presentation.view_models.answer_keys_view_model import AnswerKeysViewModel


@st.dialog("Formulário de Gabarito", width="large")
def render_answer_key_dialog(view_model: AnswerKeysViewModel, answer_key=None):
    """
    Renderiza o formulário modal para criação ou edição de um gabarito,
    exibindo a imagem da execução para facilitar a conferência.
    """
    is_editing = answer_key is not None

    col_form, col_img = st.columns([1, 1])

    with col_form:
        if is_editing:
            st.text_input("Tipo de Documento", value=answer_key.document_type, disabled=True)
            st.text_input("ID da Execução", value=answer_key.execution_id, disabled=True)
            doc_type = answer_key.document_type
            exec_id = answer_key.execution_id
        else:
            doc_type = st.selectbox("Tipo de Documento", options=["prescription", "pillpack"])

            pending_execs = view_model.get_pending_executions(doc_type)

            if not pending_execs:
                st.warning("Nenhuma execução pendente encontrada para este tipo.")
                exec_id = None
            else:
                options_map = {
                    ex.id: f"{ex.id} - {ex.start_date.strftime('%d/%m/%Y %H:%M:%S')}"
                    for ex in pending_execs
                }
                exec_id = st.selectbox(
                    "Execução",
                    options=list(options_map.keys()),
                    format_func=lambda x: options_map[x]
                )

        initial_content = json.dumps(answer_key.content, indent=4, ensure_ascii=False) if is_editing else "{\n\n}"
        content_str = st.text_area("Conteúdo (JSON)", value=initial_content, height=400)

        if st.button("Salvar", type="primary"):
            if not exec_id:
                st.error("Nenhuma execução selecionada.")
                return

            try:
                view_model.save_answer_key(
                    execution_id=exec_id,
                    document_type=doc_type,
                    content_str=content_str,
                    answer_key_id=answer_key.id if is_editing else None
                )
                st.success("Gabarito salvo com sucesso!")
                st.rerun()
            except json.JSONDecodeError:
                st.error("O conteúdo fornecido não é um JSON válido.")
            except Exception as e:
                st.error(f"Erro ao salvar: {str(e)}")

    with col_img:
        if exec_id:
            with st.spinner("Carregando imagem..."):
                try:
                    image_bytes = asyncio.run(view_model.get_execution_image(exec_id))
                    if image_bytes:
                        st.image(image_bytes, use_container_width=True)
                    else:
                        st.info("Imagem não disponível para esta execução.")
                except Exception:
                    st.error("Erro ao carregar a imagem.")
        else:
            st.info("Selecione uma execução para visualizar a imagem.")


def render_answer_keys_page(view_model: AnswerKeysViewModel) -> None:
    """
    Renderiza a página principal de manutenção de gabaritos.
    """
    st.header("Manutenção de Gabaritos")

    col_filter, col_action = st.columns([3, 1])

    with col_filter:
        doc_type_filter = st.selectbox("Filtrar por Tipo", options=["Todos", "prescription", "pillpack"])

    with col_action:
        st.write("")
        st.write("")
        if st.button("➕ Novo Gabarito", use_container_width=True):
            render_answer_key_dialog(view_model)

    filter_val = None if doc_type_filter == "Todos" else doc_type_filter
    answer_keys = view_model.get_all_answer_keys(document_type=filter_val)

    if not answer_keys:
        st.info("Nenhum gabarito encontrado.")
        return

    df = pd.DataFrame([
        {
            "ID": ak.id,
            "Execução Associada": ak.execution_id,
            "Tipo": ak.document_type,
            "Data de Criação": ak.created_at.strftime("%Y-%m-%d %H:%M:%S") if ak.created_at else "",
            "_obj": ak
        }
        for ak in answer_keys
    ])

    event = st.dataframe(
        df.drop(columns=["_obj"]),
        use_container_width=True,
        hide_index=True,
        selection_mode="single-row",
        on_select="rerun"
    )

    selected_rows = event.selection.rows

    if selected_rows:
        selected_index = selected_rows[0]
        selected_ak = df.iloc[selected_index]["_obj"]

        st.subheader("Ações para o item selecionado")
        col1, col2, _ = st.columns([1, 1, 4])

        with col1:
            if st.button("✏️ Editar Gabarito"):
                render_answer_key_dialog(view_model, selected_ak)

        with col2:
            if st.button("🗑️ Excluir Gabarito", type="primary"):
                view_model.delete_answer_key(selected_ak.id)
                st.success("Removido com sucesso!")
                st.rerun()