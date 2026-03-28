import os
from functools import partial
import streamlit as st
from dotenv import load_dotenv

from src.di.container import ApplicationContainer
from src.presentation.pages.prescriptions_page import render_prescriptions_page
from src.presentation.pages.pill_packs_page import render_pill_packs_page

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
        "api_base_url": base_url,
        "oidc_audience": os.getenv("OIDC_AUDIENCE", base_url),
        "prescription_answer_key_path": "resources/answer_keys/medical_prescription.json",
        "pill_pack_answer_key_path": "resources/answer_keys/pill_pack.json"
    })

    migration_use_case = container.run_database_migrations_use_case()
    migration_use_case.execute()

    return container


def render_placeholder_analytics() -> None:
    """
    Renderiza um conteúdo temporário para as páginas de análise.
    """
    st.title("Análise de Desempenho")
    st.info("Página em construção. Os gráficos de consumo de tokens e acurácia individual serão exibidos aqui.")


def main() -> None:
    """
    Ponto de entrada da aplicação Streamlit responsável pelo roteamento.
    """
    st.set_page_config(page_title="Dashboard de Avaliação LLM", layout="wide")

    container = init_container()

    presc_audit_page = st.Page(
        page=partial(render_prescriptions_page, container),
        title="Auditoria de Execuções",
        icon="📄",
        url_path="prescriptions_audit",
        default=True
    )

    presc_analytics_page = st.Page(
        page=render_placeholder_analytics,
        title="Análise de Desempenho",
        icon="📊",
        url_path="prescriptions_analytics"
    )

    pill_audit_page = st.Page(
        page=partial(render_pill_packs_page, container),
        title="Auditoria de Execuções",
        icon="💊",
        url_path="pillpacks_audit"
    )

    pill_analytics_page = st.Page(
        page=render_placeholder_analytics,
        title="Análise de Desempenho",
        icon="📊",
        url_path="pillpacks_analytics"
    )

    pages = {
        "Prescrições Médicas": [presc_audit_page, presc_analytics_page],
        "Cartelas de Comprimidos": [pill_audit_page, pill_analytics_page]
    }

    pg = st.navigation(pages)
    pg.run()


if __name__ == "__main__":
    main()