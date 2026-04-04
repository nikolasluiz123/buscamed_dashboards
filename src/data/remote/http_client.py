import asyncio
import httpx
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class HttpClient(ABC):
    """
    Abstração para o cliente HTTP.
    """

    @abstractmethod
    async def get(self, url: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None,
                  auth: Any = None) -> Any:
        """
        Executa uma requisição HTTP GET e retorna o corpo da resposta em formato JSON.
        """
        pass

    @abstractmethod
    async def get_bytes(self, url: str, headers: Optional[Dict[str, str]] = None,
                        params: Optional[Dict[str, Any]] = None, auth: Any = None) -> bytes:
        """
        Executa uma requisição HTTP GET e retorna o corpo da resposta em formato de bytes.
        """
        pass


class HttpxHttpClient(HttpClient):
    """
    Implementação do HttpClient utilizando a biblioteca httpx.
    """

    def __init__(self, max_retries: int = 1):
        """
        Inicializa o cliente HTTP.

        Args:
            max_retries (int): Número máximo de tentativas em caso de erro de autorização ou falha de rede.
        """
        self._max_retries = max_retries

    async def get(self, url: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None,
                  auth: Any = None) -> Any:
        """
        Executa uma requisição HTTP GET e retorna o corpo da resposta em formato JSON.
        """
        for attempt in range(self._max_retries + 1):
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, params=params, auth=auth)

                if response.status_code == 401 and attempt < self._max_retries:
                    await asyncio.sleep(0.5)
                    continue

                response.raise_for_status()
                return response.json()

    async def get_bytes(self, url: str, headers: Optional[Dict[str, str]] = None,
                        params: Optional[Dict[str, Any]] = None, auth: Any = None) -> bytes:
        """
        Executa uma requisição HTTP GET e retorna o corpo da resposta em formato de bytes.
        """
        for attempt in range(self._max_retries + 1):
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, params=params, auth=auth)

                if response.status_code == 401 and attempt < self._max_retries:
                    await asyncio.sleep(0.5)
                    continue

                response.raise_for_status()
                return response.read()