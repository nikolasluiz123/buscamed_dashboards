# src/data/remote/remote_datasource.py

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
        """
        pass

    def _get_oidc_token(self) -> str:
        """
        Obtém o token de autenticação OIDC.
        """
        request = google.auth.transport.requests.Request()
        return google.oauth2.id_token.fetch_id_token(request, self.audience)

    @abstractmethod
    async def fetch_executions(self, since_date: Optional[str] = None) -> List[Execution]:
        """
        Busca a lista de execuções remotas.
        """
        pass

    @abstractmethod
    async def fetch_image(self, execution_id: str) -> bytes:
        """
        Faz o download da imagem relacionada a uma execução através do seu ID.
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
        return self._base_url

    async def fetch_executions(self, since_date: Optional[str] = None) -> List[Execution]:
        """
        Busca o histórico de execuções de receitas médicas na API.
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
        return self._base_url

    async def fetch_executions(self, since_date: Optional[str] = None) -> List[Execution]:
        """
        Busca o histórico de execuções de cartelas de comprimidos na API.
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
        """
        token = self._get_oidc_token()
        headers = {"Authorization": f"Bearer {token}"}
        params = {"executionId": execution_id}
        url = f"{self.base_url}/v1/pillpack/image"

        return await self.http_client.get_bytes(url, headers=headers, params=params)