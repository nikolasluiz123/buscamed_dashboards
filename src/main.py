import os
import streamlit as st
from dotenv import load_dotenv

from src.di.container import ApplicationContainer

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


def main():
    container = init_container()

    st.title("Dashboard de Avaliação LLM")
    st.write("Container inicializado e banco de dados atualizado com sucesso!")

    # Exemplo prático de como chamar um UseCase a partir do container:
    # use_case = container.calculate_prescription_accuracy_use_case()
    # accuracy = use_case.execute()


if __name__ == "__main__":
    main()