import os
from typing import Dict

class QueryManager:
    """
    Gerencia a leitura e o cache de consultas SQL a partir de arquivos físicos.
    """
    def __init__(self, queries_dir: str):
        self._queries_dir = queries_dir
        self._cache: Dict[str, str] = {}

    def get(self, query_name: str) -> str:
        """
        Retorna o conteúdo de um arquivo .sql pelo seu nome (sem a extensão).
        Utiliza cache em memória para evitar leituras repetidas em disco.
        """
        if query_name in self._cache:
            return self._cache[query_name]

        file_path = os.path.join(self._queries_dir, f"{query_name}.sql")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Arquivo de query não encontrado: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            query_content = f.read()
            self._cache[query_name] = query_content
            return query_content