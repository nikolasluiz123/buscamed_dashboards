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

    GET_LAST_SYNC_DATE = "SELECT MAX(start_date) FROM executions WHERE execution_type = ?"

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