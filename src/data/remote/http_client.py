from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import httpx

class HttpClient(ABC):
    """
    Abstração para o cliente HTTP.
    """
    @abstractmethod
    async def get(self, url: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None) -> Any:
        pass

class HttpxHttpClient(HttpClient):
    """
    Implementação do HttpClient utilizando a biblioteca httpx.
    """
    async def get(self, url: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None) -> Any:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()