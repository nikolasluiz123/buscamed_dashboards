import streamlit as st
from src.di.container import ApplicationContainer


def render_pill_packs_page(container: ApplicationContainer) -> None:
    """
    Renderiza a página principal de avaliação de Cartelas de Comprimidos.
    """
    st.title("Avaliação: Cartelas de Comprimidos")
    st.write("Em construção...")