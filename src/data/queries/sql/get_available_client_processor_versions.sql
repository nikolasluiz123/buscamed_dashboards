SELECT DISTINCT client_processor_version FROM executions
WHERE execution_type = ? AND client_processor_version IS NOT NULL AND client_processor_version != '';