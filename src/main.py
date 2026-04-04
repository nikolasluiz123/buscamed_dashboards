import os
from functools import partial
import streamlit as st
from dotenv import load_dotenv

from src.di.container import ApplicationContainer
from src.presentation.pages.answer_keys_page import render_answer_keys_page
from src.presentation.pages.prescriptions_page import render_prescriptions_page
from src.presentation.pages.pill_packs_page import render_pill_packs_page
from src.presentation.pages.prescriptions_analytics_page import render_prescriptions_analytics_page
from src.presentation.pages.pill_packs_analytics_page import render_pill_packs_analytics_page

load_dotenv()


@st.cache_resource
def init_container() -> ApplicationContainer:
    """
    Inicializa o container de injeção de dependências e aplica as configurações.
    """
    container = ApplicationContainer()

    base_url = os.getenv("API_BASE_URL", "http://192.168.0.41:8080")

    container.config.from_dict({
        "db_path": os.getenv("DB_PATH", "buscamed_analytics.duckdb"),
        "queries_dir": "src/data/queries/sql",
        "migrations_dir": "src/data/migrations",
        "api_base_url": base_url,
        "oidc_audience": os.getenv("OIDC_AUDIENCE", base_url),
        "prescription_answer_key_path": "resources/answer_keys/medical_prescription.json",
        "pill_pack_answer_key_path": "resources/answer_keys/pill_pack.json"
    })

    migration_use_case = container.run_database_migrations_use_case()
    migration_use_case.execute()

    return container


def main() -> None:
    """
    Ponto de entrada da aplicação Streamlit responsável pelo roteamento.
    """
    st.set_page_config(page_title="Dashboard de Avaliação LLM", layout="wide")

    container = init_container()

    app_env = os.getenv("APP_ENV", "local")

    if app_env == "remote":
        auth_manager = container.auth_manager()
        is_authenticated = auth_manager.login()

        if not is_authenticated:
            if st.session_state.get("authentication_status") is False:
                st.error("Usuário ou senha incorretos")
            elif st.session_state.get("authentication_status") is None:
                st.warning("Por favor, insira suas credenciais")
            return
        else:
            auth_manager.logout()

    presc_view_model = container.prescriptions_view_model()
    pill_view_model = container.pill_packs_view_model()

    presc_analytics_vm = container.prescriptions_analytics_view_model()
    pill_analytics_vm = container.pill_packs_analytics_view_model()

    answer_keys_vm = container.answer_keys_view_model()

    presc_audit_page = st.Page(
        page=partial(render_prescriptions_page, presc_view_model),
        title="Auditoria de Execuções",
        icon="📄",
        url_path="prescriptions_audit",
        default=True
    )

    presc_analytics_page = st.Page(
        page=partial(render_prescriptions_analytics_page, presc_analytics_vm),
        title="Análise de Desempenho",
        icon="📊",
        url_path="prescriptions_analytics"
    )

    pill_audit_page = st.Page(
        page=partial(render_pill_packs_page, pill_view_model),
        title="Auditoria de Execuções",
        icon="💊",
        url_path="pillpacks_audit"
    )

    pill_analytics_page = st.Page(
        page=partial(render_pill_packs_analytics_page, pill_analytics_vm),
        title="Análise de Desempenho",
        icon="📊",
        url_path="pillpacks_analytics"
    )

    answer_keys_page = st.Page(
        page=partial(render_answer_keys_page, answer_keys_vm),
        title="Manutenção de Gabaritos",
        icon="📋",
        url_path="answer_keys_maintenance"
    )

    pages = {
        "Prescrições Médicas": [presc_audit_page, presc_analytics_page],
        "Cartelas de Comprimidos": [pill_audit_page, pill_analytics_page],
        "Gabaritos": [answer_keys_page]
    }

    pg = st.navigation(pages)
    pg.run()


if __name__ == "__main__":
    main()