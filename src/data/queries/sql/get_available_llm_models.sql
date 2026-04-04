SELECT DISTINCT llm_model FROM executions
WHERE execution_type = ? AND llm_model IS NOT NULL AND llm_model != '';