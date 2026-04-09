SELECT
    id,
    execution_type,
    processing_type,
    input_text,
    input_tokens,
    output_tokens,
    result,
    success,
    start_date,
    end_date,
    storage_path,
    prompt,
    client_processor_version,
    llm_model
FROM executions
WHERE id = ?;