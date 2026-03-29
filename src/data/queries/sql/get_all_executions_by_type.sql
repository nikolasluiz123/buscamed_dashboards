SELECT * FROM executions
WHERE execution_type = ?
{filters}
ORDER BY start_date DESC;