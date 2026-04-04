INSERT INTO answer_keys (id, execution_id, document_type, content)
VALUES (COALESCE(?, nextval('seq_answer_keys_id')), ?, ?, ?)
ON CONFLICT (id) DO UPDATE SET
    execution_id = excluded.execution_id,
    document_type = excluded.document_type,
    content = excluded.content
RETURNING id, created_at;