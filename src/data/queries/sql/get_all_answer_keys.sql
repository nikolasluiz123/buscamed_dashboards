SELECT id, execution_id, document_type, content, created_at
FROM answer_keys
{filters}
ORDER BY created_at DESC;