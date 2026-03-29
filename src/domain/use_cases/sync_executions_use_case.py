from datetime import datetime, timezone
from src.data.repositories import ExecutionRepository


class SyncExecutionsUseCase:
    """
    Caso de uso para sincronizar as execuções da fonte remota para o banco de dados local.
    """

    def __init__(self, repository: ExecutionRepository):
        self.repository = repository

    async def execute(self) -> int:
        sync_requested_at = datetime.now(timezone.utc)

        last_sync_date = self.repository.get_last_sync_date()
        new_executions = await self.repository.fetch_remote_executions(last_sync_date)

        if not new_executions:
            self.repository.update_last_sync_date(sync_requested_at)
            return 0

        self.repository.save_executions(new_executions)
        self.repository.update_last_sync_date(sync_requested_at)

        return len(new_executions)