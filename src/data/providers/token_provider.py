import os
import subprocess
from abc import ABC, abstractmethod
import google.auth.transport.requests
import google.oauth2.id_token


class TokenProvider(ABC):
    """
    Interface para o fornecimento de tokens de autenticação.
    """

    @abstractmethod
    def get_token(self) -> str:
        pass


class OIDCTokenProvider(TokenProvider):
    """
    Fornecedor de tokens OIDC integrado com o Google Cloud.
    """

    def __init__(self, audience: str):
        self.audience = audience

    def get_token(self) -> str:
        """
        Obtém o token OIDC, utilizando impersonation localmente ou o padrão em produção.
        """
        if os.getenv("APP_ENV") == "local":
            service_account = os.getenv("IMPERSONATE_SERVICE_ACCOUNT")
            if service_account:
                command = [
                    "gcloud", "auth", "print-identity-token",
                    f"--impersonate-service-account={service_account}",
                    f"--audiences={self.audience}"
                ]

                result = subprocess.run(command, capture_output=True, text=True, check=False, shell=True)

                if result.returncode != 0:
                    raise RuntimeError(f"Falha ao obter o token OIDC localmente: {result.stderr}")

                return result.stdout.strip()

        request = google.auth.transport.requests.Request()
        return google.oauth2.id_token.fetch_id_token(request, self.audience)