CREATE TABLE IF NOT EXISTS executions
(
    id VARCHAR PRIMARY KEY,
    execution_type VARCHAR,
    input_tokens INTEGER,
    output_tokens INTEGER,
    result VARCHAR,
    success BOOLEAN,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    storage_image_path VARCHAR,
    prompt VARCHAR
);