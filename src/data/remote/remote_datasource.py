import os
import subprocess
from abc import ABC, abstractmethod
from typing import List, Optional
import google.auth.transport.requests
import google.oauth2.id_token

from src.data.dtos import LLMExecutionDTO
from src.data.remote.http_client import HttpClient
from src.domain.entities import Execution


class BaseAPIExecutionDataSource(ABC):
    """
    Implementação base para o acesso a dados remotos contendo a lógica de autenticação OIDC.
    """

    def __init__(self, http_client: HttpClient, audience: str):
        self.http_client = http_client
        self.audience = audience

    @property
    @abstractmethod
    def base_url(self) -> str:
        """
        URL base da API a ser definida pelas classes filhas.

        Returns:
            str: A URL base da API.
        """
        pass

    def _get_oidc_token(self) -> str:
        """
        Obtém o token de autenticação OIDC.

        Se a variável de ambiente APP_ENV for 'local' e a variável
        IMPERSONATE_SERVICE_ACCOUNT estiver definida, utiliza o Google Cloud CLI
        para gerar o token. Caso contrário, utiliza o método padrão da biblioteca.

        Returns:
            str: O token OIDC gerado.

        Raises:
            RuntimeError: Se a execução do comando do Google Cloud CLI falhar no ambiente local.
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

    @abstractmethod
    async def fetch_executions(self, since_date: Optional[str] = None) -> List[Execution]:
        """
        Busca a lista de execuções remotas.

        Args:
            since_date (Optional[str]): Filtro opcional a partir de uma data específica.

        Returns:
            List[Execution]: Lista de execuções retornadas pela API.
        """
        pass

    @abstractmethod
    async def fetch_image(self, execution_id: str) -> bytes:
        """
        Faz o download da imagem relacionada a uma execução através do seu ID.

        Args:
            execution_id (str): Identificador único da execução.

        Returns:
            bytes: O conteúdo da imagem em array de bytes.
        """
        pass


class PrescriptionRemoteDataSource(BaseAPIExecutionDataSource):
    """
    Implementação específica para buscar dados remotos de Receitas Médicas.
    """

    def __init__(self, http_client: HttpClient, base_url: str, audience: str):
        super().__init__(http_client=http_client, audience=audience)
        self._base_url = base_url

    @property
    def base_url(self) -> str:
        """
        Retorna a URL base do serviço de receitas.

        Returns:
            str: URL base configurada.
        """
        return self._base_url

    async def fetch_executions(self, since_date: Optional[str] = None) -> List[Execution]:
        """
        Busca o histórico de execuções de receitas médicas na API.

        Args:
            since_date (Optional[str]): Filtro opcional a partir de uma data específica.

        Returns:
            List[Execution]: Lista de entidades de execução de receitas.
        """
        token = self._get_oidc_token()
        headers = {"Authorization": f"Bearer {token}"}
        params = {"startDate": since_date} if since_date else {}
        url = f"{self.base_url}/v1/prescription/history"

        data = await self.http_client.get(url, headers=headers, params=params)
        return [LLMExecutionDTO(**item).to_domain("prescription") for item in data]

    async def fetch_image(self, execution_id: str) -> bytes:
        """
        Baixa a imagem processada de uma receita médica através da API utilizando o ID da execução.

        Args:
            execution_id (str): Identificador único da execução.

        Returns:
            bytes: O conteúdo da imagem em array de bytes.
        """
        token = self._get_oidc_token()
        headers = {"Authorization": f"Bearer {token}"}
        params = {"executionId": execution_id}
        url = f"{self.base_url}/v1/prescription/image"

        return await self.http_client.get_bytes(url, headers=headers, params=params)


class PillPackRemoteDataSource(BaseAPIExecutionDataSource):
    """
    Implementação específica para buscar dados remotos de Cartelas de Comprimidos.
    """

    def __init__(self, http_client: HttpClient, base_url: str, audience: str):
        super().__init__(http_client=http_client, audience=audience)
        self._base_url = base_url

    @property
    def base_url(self) -> str:
        """
        Retorna a URL base do serviço de cartelas.

        Returns:
            str: URL base configurada.
        """
        return self._base_url

    async def fetch_executions(self, since_date: Optional[str] = None) -> List[Execution]:
        """
        Busca o histórico de execuções de cartelas de comprimidos na API.

        Args:
            since_date (Optional[str]): Filtro opcional a partir de uma data específica.

        Returns:
            List[Execution]: Lista de entidades de execução de cartelas.
        """
        token = self._get_oidc_token()
        headers = {"Authorization": f"Bearer {token}"}
        params = {"startDate": since_date} if since_date else {}
        url = f"{self.base_url}/v1/pillpack/history"

        data = await self.http_client.get(url, headers=headers, params=params)
        return [LLMExecutionDTO(**item).to_domain("pillpack") for item in data]

    async def fetch_image(self, execution_id: str) -> bytes:
        """
        Baixa a imagem processada de uma cartela de comprimidos através da API utilizando o ID da execução.

        Args:
            execution_id (str): Identificador único da execução.

        Returns:
            bytes: O conteúdo da imagem em array de bytes.
        """
        token = self._get_oidc_token()
        headers = {"Authorization": f"Bearer {token}"}
        params = {"executionId": execution_id}
        url = f"{self.base_url}/v1/pillpack/image"

        return await self.http_client.get_bytes(url, headers=headers, params=params)