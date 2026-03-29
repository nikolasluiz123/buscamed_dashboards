class ExecutionQueries:
    """
    Armazena as operações SQL relacionadas às execuções.
    """
    CREATE_MIGRATION_TABLE = """
                             CREATE TABLE IF NOT EXISTS schema_migrations \
                             ( \
                                 version \
                                 VARCHAR \
                                 PRIMARY \
                                 KEY, \
                                 applied_at \
                                 TIMESTAMP \
                                 DEFAULT \
                                 CURRENT_TIMESTAMP
                             ) \
                             """

    CHECK_MIGRATION = "SELECT version FROM schema_migrations WHERE version = ?"

    INSERT_MIGRATION = "INSERT INTO schema_migrations (version) VALUES (?)"

    GET_LAST_SYNC_DATE = "SELECT last_sync_date FROM sync_control WHERE execution_type = ?"

    UPSERT_SYNC_DATE = """
                       INSERT INTO sync_control (execution_type, last_sync_date)
                       VALUES (?, ?) ON CONFLICT (execution_type) DO
                       UPDATE SET last_sync_date = excluded.last_sync_date
                       """

    UPSERT_EXECUTION = """
                       INSERT INTO executions (id, execution_type, input_tokens, output_tokens, result, \
                                               success, start_date, end_date, storage_image_path, prompt) \
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT (id) DO \
                       UPDATE SET
                           result = excluded.result, \
                           success = excluded.success, \
                           prompt = excluded.prompt \
                       """

    GET_ALL_EXECUTIONS_BY_TYPE = "SELECT * FROM executions WHERE execution_type = ?"

    GET_AVAILABLE_PROMPTS = "SELECT DISTINCT prompt FROM executions WHERE execution_type = ? AND prompt IS NOT NULL AND prompt != ''"