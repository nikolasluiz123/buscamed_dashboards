from abc import ABC, abstractmethod
from typing import Dict, Any


class AnswerKeyProvider(ABC):
    """
    Contrato para fornecimento de gabaritos de validação.
    """

    @abstractmethod
    def get_answer_keys(self) -> Dict[str, Any]:
        """
        Recupera os gabaritos mapeados por seus respectivos identificadores únicos.
        """
        pass