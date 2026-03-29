import httpx
from src.data.providers.token_provider import TokenProvider

class OIDCAuth(httpx.Auth):
    """
    Interceptor de autenticação para injetar o token Bearer nas requisições HTTPX.
    """
    def __init__(self, token_provider: TokenProvider):
        self.token_provider = token_provider

    def auth_flow(self, request: httpx.Request):
        """
        Fluxo de injeção de cabeçalho de autenticação.
        """
        token = self.token_provider.get_token()
        request.headers["Authorization"] = f"Bearer {token}"
        yield request