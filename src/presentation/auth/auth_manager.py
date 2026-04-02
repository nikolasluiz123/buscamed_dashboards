import streamlit as st
import streamlit_authenticator as stauth

class StreamlitAuthManager:
    """
    Gerenciador de autenticação de usuários para o Streamlit.
    """

    def __init__(self, credentials: dict, cookie_name: str, cookie_key: str, cookie_expiry_days: int):
        self.authenticator = stauth.Authenticate(
            credentials=credentials,
            cookie_name=cookie_name,
            cookie_key=cookie_key,
            cookie_expiry_days=cookie_expiry_days
        )

    def login(self) -> bool:
        """
        Renderiza o componente de login e retorna o estado atual da autenticação.

        Returns:
            bool: True se o usuário estiver autenticado, False caso contrário.
        """
        self.authenticator.login(location='main')
        return st.session_state.get("authentication_status", False)

    def logout(self) -> None:
        """
        Renderiza o botão de logout na barra lateral da aplicação.
        """
        self.authenticator.logout(location='sidebar')