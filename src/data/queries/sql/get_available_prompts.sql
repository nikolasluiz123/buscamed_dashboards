SELECT DISTINCT prompt FROM executions
WHERE execution_type = ? AND prompt IS NOT NULL AND prompt != '';