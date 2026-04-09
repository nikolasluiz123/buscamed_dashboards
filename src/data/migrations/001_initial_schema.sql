CREATE TABLE IF NOT EXISTS executions
(
    id VARCHAR PRIMARY KEY,
    execution_type VARCHAR,
    processing_type VARCHAR,
    input_text VARCHAR,
    input_tokens INTEGER,
    output_tokens INTEGER,
    result VARCHAR,
    success BOOLEAN,
    start_date TIMESTAMP WITH TIME ZONE,
    end_date TIMESTAMP WITH TIME ZONE,
    storage_path VARCHAR,
    prompt VARCHAR,
    client_processor_version VARCHAR NOT NULL,
    llm_model VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS sync_control
(
    execution_type VARCHAR PRIMARY KEY,
    last_sync_date TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE SEQUENCE IF NOT EXISTS seq_answer_keys_id;

CREATE TABLE IF NOT EXISTS answer_keys
(
    id INTEGER DEFAULT nextval('seq_answer_keys_id') PRIMARY KEY,
    execution_id VARCHAR NOT NULL REFERENCES executions(id),
    document_type VARCHAR NOT NULL,
    content JSON NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);