CREATE TABLE answer_keys_backup AS SELECT * FROM answer_keys;

DROP TABLE answer_keys;

ALTER TABLE executions RENAME COLUMN storage_image_path TO storage_path;

CREATE TABLE answer_keys
(
    id INTEGER DEFAULT nextval('seq_answer_keys_id') PRIMARY KEY,
    execution_id VARCHAR NOT NULL REFERENCES executions(id),
    document_type VARCHAR NOT NULL,
    content JSON NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO answer_keys (id, execution_id, document_type, content, created_at)
SELECT id, execution_id, document_type, content, created_at FROM answer_keys_backup;

DROP TABLE answer_keys_backup;