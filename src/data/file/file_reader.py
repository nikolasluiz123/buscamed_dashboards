import json
from abc import ABC, abstractmethod
from typing import Dict, Any

class FileReader(ABC):
    """
    Abstração para leitura de arquivos locais.
    """
    @abstractmethod
    def load_json(self, file_path: str) -> Dict[str, Any]:
        pass

class LocalFileReader(FileReader):
    """
    Implementação do FileReader para leitura do sistema de arquivos.
    """
    def load_json(self, file_path: str) -> Dict[str, Any]:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return {item['id']: item for item in data}