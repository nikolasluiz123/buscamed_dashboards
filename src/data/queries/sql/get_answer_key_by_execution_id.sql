SELECT id, execution_id, document_type, content, created_at
FROM answer_keys
WHERE execution_id = ?;