from abc import ABC, abstractmethod
from typing import List, Optional
import google.auth.transport.requests
import google.oauth2.id_token

from src.data.dtos import LLMExecutionDTO
from src.data.remote.http_client import HttpClient
from src.domain.entities import Execution


class RemoteDataSource(ABC):
    """
    Abstração para o acesso a dados remotos.
    """

    @abstractmethod
    async def fetch_executions(self, since_date: Optional[str] = None) -> List[Execution]:
        pass


class BaseAPIExecutionDataSource(RemoteDataSource):
    """
    Implementação base do RemoteDataSource contendo a lógica de autenticação OIDC.
    """

    def __init__(self, http_client: HttpClient, base_url: str, audience: str, endpoint_path: str, execution_type: str):
        self.http_client = http_client
        self.base_url = base_url
        self.audience = audience
        self.endpoint_path = endpoint_path
        self.execution_type = execution_type

    def _get_oidc_token(self) -> str:
        request = google.auth.transport.requests.Request()
        return google.oauth2.id_token.fetch_id_token(request, self.audience)

    async def fetch_executions(self, since_date: Optional[str] = None) -> List[Execution]:
        token = self._get_oidc_token()
        headers = {"Authorization": f"Bearer {token}"}
        params = {"startDate": since_date} if since_date else {}
        url = f"{self.base_url}{self.endpoint_path}"

        data = await self.http_client.get(url, headers=headers, params=params)
        return [LLMExecutionDTO(**item).to_domain(self.execution_type) for item in data]


class PrescriptionRemoteDataSource(BaseAPIExecutionDataSource):
    """
    Implementação específica para buscar dados remotos de Receitas Médicas.
    """

    def __init__(self, http_client: HttpClient, base_url: str, audience: str):
        super().__init__(
            http_client=http_client,
            base_url=base_url,
            audience=audience,
            endpoint_path="/v1/prescription/history",
            execution_type="prescription"
        )


class PillPackRemoteDataSource(BaseAPIExecutionDataSource):
    """
    Implementação específica para buscar dados remotos de Cartelas de Comprimidos.
    """

    def __init__(self, http_client: HttpClient, base_url: str, audience: str):
        super().__init__(
            http_client=http_client,
            base_url=base_url,
            audience=audience,
            endpoint_path="/v1/pillpack/history",
            execution_type="pillpack"
        )