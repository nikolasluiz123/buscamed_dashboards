SELECT executions.*
FROM executions
INNER JOIN answer_keys ON executions.id = answer_keys.execution_id
WHERE execution_type = ?
{filters}
ORDER BY start_date DESC;