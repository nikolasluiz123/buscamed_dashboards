from abc import ABC
from typing import List, Optional
from datetime import datetime

from src.data.dtos import LLMExecutionDTO
from src.data.remote.http_client import HttpClient
from src.data.remote.auth_interceptor import OIDCAuth
from src.domain.entities import Execution


class BuscaMedRemoteDataSource(ABC):
    """
    Classe base para comunicação com a API do BuscaMed.
    Encapsula o cliente HTTP, a URL base e o interceptor de autenticação.
    """
    def __init__(self, http_client: HttpClient, base_url: str, auth_interceptor: OIDCAuth):
        self._http_client = http_client
        self._base_url = base_url
        self._auth = auth_interceptor


class ExecutionRemoteDataSource(BuscaMedRemoteDataSource):
    """
    Data Source genérico para buscar execuções.
    O contexto ('prescription' ou 'pillpack') é definido na inicialização para montar a rota.
    """
    def __init__(self, http_client: HttpClient, base_url: str, auth_interceptor: OIDCAuth, execution_context: str):
        super().__init__(http_client, base_url, auth_interceptor)
        self._execution_context = execution_context

    async def fetch_executions(self, since_date: Optional[datetime] = None) -> List[Execution]:
        """
        Busca o histórico de execuções na API com base no contexto definido.
        """
        formatted_date = None
        if since_date:
            formatted_date = since_date.isoformat().replace("+00:00", "Z")

        params = {"startDate": formatted_date} if formatted_date else {}
        url = f"{self._base_url}/v1/{self._execution_context}/history"

        data = await self._http_client.get(url, params=params, auth=self._auth)
        return [LLMExecutionDTO(**item).to_domain(self._execution_context) for item in data]

    async def fetch_image(self, execution_id: str) -> bytes:
        """
        Baixa a imagem processada de uma execução.
        """
        params = {"executionId": execution_id}
        url = f"{self._base_url}/v1/{self._execution_context}/image"

        return await self._http_client.get_bytes(url, params=params, auth=self._auth)