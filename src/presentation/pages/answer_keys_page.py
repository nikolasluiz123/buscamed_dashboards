import json
import asyncio
import streamlit as st
import pandas as pd
from datetime import timedelta
from streamlit_ace import st_ace
from src.presentation.view_models.answer_keys_view_model import AnswerKeysViewModel


def get_prescription_template() -> str:
    """
    Retorna o template JSON base para prescrições estruturado a partir do schema definido.

    Returns:
        str: JSON formatado contendo a estrutura vazia de medicamentos.
    """
    template = {
        "medicamentos": [
            {
                "nome": None,
                "apresentacao_dosagem": {
                    "valor": None,
                    "unidade": None
                },
                "dose": {
                    "valor": None,
                    "unidade": None
                },
                "frequencia": {
                    "intervalo": None,
                    "unidade": None,
                    "texto_orientacao": None
                },
                "duracao": {
                    "valor": None,
                    "unidade": None,
                    "uso_continuo": None
                },
                "quantidade_total_prescrita": {
                    "valor": None,
                    "unidade": None
                }
            }
        ]
    }
    return json.dumps(template, indent=4, ensure_ascii=False)


@st.cache_data(max_entries=200, ttl=timedelta(hours=2), show_spinner=False)
def get_cached_execution_image(_view_model: AnswerKeysViewModel, execution_id: str) -> bytes:
    """
    Recupera os bytes da imagem vinculada à execução utilizando cache de dados.

    Args:
        _view_model (AnswerKeysViewModel): A ViewModel contendo a lógica de acesso à imagem.
        execution_id (str): Identificador único da execução utilizado como chave de cache.

    Returns:
        bytes: Arquivo de imagem em formato de bytes ou None caso não encontrada.
    """
    return asyncio.run(_view_model.get_execution_image(execution_id))


@st.dialog("Visualização Ampliada", width="large")
def render_fullscreen_image_dialog(image_bytes: bytes):
    """
    Renderiza um modal dedicado para a visualização da imagem em maior escala.

    Args:
        image_bytes (bytes): O arquivo de imagem em bytes a ser exibido.
    """
    st.image(image_bytes, width='stretch')


@st.dialog("Formulário de Gabarito", width="large")
def render_answer_key_dialog(view_model: AnswerKeysViewModel, answer_key=None):
    """
    Renderiza o formulário modal para criação ou edição de um gabarito,
    exibindo a imagem da execução para facilitar a conferência.
    """
    st.markdown(
        """
        <style>
        div[data-testid="stDialog"] div[role="dialog"] {
            width: 90vw !important;
            max-width: 90vw !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

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

        if is_editing:
            initial_content = json.dumps(answer_key.content, indent=4, ensure_ascii=False)
        else:
            if doc_type == "prescription":
                initial_content = get_prescription_template()
            else:
                initial_content = "{\n\n}"

        st.caption("Conteúdo (JSON)")
        content_str = st_ace(
            value=initial_content,
            language="json",
            theme="monokai",
            keybinding="vscode",
            height=400,
            show_gutter=True,
            show_print_margin=False,
            wrap=True,
            auto_update=True
        )

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
                    image_bytes = get_cached_execution_image(
                        _view_model=view_model,
                        execution_id=exec_id
                    )
                    if image_bytes:
                        if st.button("🔍 Expandir Imagem em Tela Cheia", width='stretch'):
                            render_fullscreen_image_dialog(image_bytes)

                        st.image(image_bytes, width='stretch')
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
        if st.button("➕ Novo Gabarito", width='stretch'):
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
        width='stretch',
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