import os
from typing import List

from src.data.queries.query_manager import QueryManager
from src.data.local.connection_factory import DuckDBConnectionFactory


class DatabaseMigrator:
    """
    Gerencia a execução de scripts SQL para evolução do esquema do banco de dados lendo de arquivos .sql.
    """

    def __init__(self, connection_factory: DuckDBConnectionFactory, migrations_dir: str, query_manager: QueryManager):
        self._connection_factory = connection_factory
        self._migrations_dir = migrations_dir
        self._query_manager = query_manager

    def _get_migration_files(self) -> List[str]:
        """
        Lista e ordena os arquivos .sql do diretório de migrações.
        """
        if not os.path.exists(self._migrations_dir):
            return []

        files = [f for f in os.listdir(self._migrations_dir) if f.endswith('.sql')]
        return sorted(files)

    def run_migrations(self) -> None:
        """
        Lê e aplica migrações pendentes no banco de dados.
        """
        with self._connection_factory.get_connection() as con:
            con.execute(self._query_manager.get('create_migration_table'))

            migration_files = self._get_migration_files()

            for filename in migration_files:
                version = os.path.splitext(filename)[0]

                result = con.execute(self._query_manager.get('check_migration'), [version]).fetchone()
                if not result:
                    file_path = os.path.join(self._migrations_dir, filename)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        script = f.read()

                    con.execute("BEGIN TRANSACTION")
                    con.execute(script)
                    con.execute(self._query_manager.get('insert_migration'), [version])
                    con.execute("COMMIT")