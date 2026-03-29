from typing import Dict, Any
from src.domain.ports.answer_key_provider import AnswerKeyProvider
from src.data.file.file_reader import FileReader

class FileAnswerKeyProvider(AnswerKeyProvider):
    """
    Implementação de AnswerKeyProvider utilizando sistema de arquivos local.
    """

    def __init__(self, file_reader: FileReader, file_path: str):
        self._file_reader = file_reader
        self._file_path = file_path

    def get_answer_keys(self) -> Dict[str, Any]:
        """
        Lê o arquivo local utilizando o FileReader injetado.
        """
        try:
            return self._file_reader.load_json(self._file_path)
        except FileNotFoundError:
            return {}