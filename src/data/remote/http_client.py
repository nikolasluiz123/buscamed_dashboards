from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import httpx

class HttpClient(ABC):
    """
    Abstração para o cliente HTTP.
    """
    @abstractmethod
    async def get(self, url: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, auth: Any = None) -> Any:
        pass

    @abstractmethod
    async def get_bytes(self, url: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, auth: Any = None) -> bytes:
        pass


class HttpxHttpClient(HttpClient):
    """
    Implementação do HttpClient utilizando a biblioteca httpx.
    """
    async def get(self, url: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, auth: Any = None) -> Any:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params, auth=auth)
            response.raise_for_status()
            return response.json()

    async def get_bytes(self, url: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, auth: Any = None) -> bytes:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params, auth=auth)
            response.raise_for_status()
            return response.read()