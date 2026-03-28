from src.data.database_migrator import DatabaseMigrator

class RunDatabaseMigrationsUseCase:
    """
    Caso de uso responsável por garantir que o banco de dados local esteja na versão mais atual.
    """

    def __init__(self, migrator: DatabaseMigrator):
        self.migrator = migrator

    def execute(self) -> None:
        self.migrator.run_migrations()