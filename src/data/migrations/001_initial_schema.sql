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
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    storage_image_path VARCHAR,
    prompt VARCHAR,
    client_processor_version VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS sync_control
(
    execution_type VARCHAR PRIMARY KEY,
    last_sync_date TIMESTAMP NOT NULL
);