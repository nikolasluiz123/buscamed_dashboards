import duckdb
from typing import Dict

from src.data.queries import ExecutionQueries


class DatabaseMigrator:
    """
    Gerencia a execução de scripts SQL para evolução do esquema do banco de dados.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._migrations: Dict[str, str] = {
            "001_initial_schema": """
                                  CREATE TABLE IF NOT EXISTS executions
                                  (
                                      id VARCHAR PRIMARY KEY,
                                      execution_type VARCHAR,
                                      input_tokens INTEGER,
                                      output_tokens INTEGER,
                                      result VARCHAR,
                                      success BOOLEAN,
                                      start_date TIMESTAMP,
                                      end_date TIMESTAMP,
                                      storage_image_path VARCHAR,
                                      prompt VARCHAR
                                  )
                                  """,
            "002_sync_control_schema": """
                                       CREATE TABLE IF NOT EXISTS sync_control
                                       (
                                           execution_type VARCHAR PRIMARY KEY,
                                           last_sync_date TIMESTAMP NOT NULL
                                       )
                                       """
        }

    def run_migrations(self) -> None:
        """
        Aplica migrações pendentes no banco de dados.
        """
        with duckdb.connect(self.db_path) as con:
            con.execute(ExecutionQueries.CREATE_MIGRATION_TABLE)

            for version, script in self._migrations.items():
                result = con.execute(ExecutionQueries.CHECK_MIGRATION, [version]).fetchone()
                if not result:
                    con.execute("BEGIN TRANSACTION")
                    con.execute(script)
                    con.execute(ExecutionQueries.INSERT_MIGRATION, [version])
                    con.execute("COMMIT")