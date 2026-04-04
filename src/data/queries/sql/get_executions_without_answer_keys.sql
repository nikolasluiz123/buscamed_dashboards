SELECT
    e.id,
    e.execution_type,
    e.processing_type,
    e.input_text,
    e.input_tokens,
    e.output_tokens,
    e.result,
    e.success,
    e.start_date,
    e.end_date,
    e.storage_image_path,
    e.prompt,
    e.client_processor_version,
    e.llm_model
FROM executions e
LEFT JOIN answer_keys ak ON e.id = ak.execution_id
WHERE ak.id IS NULL AND e.execution_type = ?
ORDER BY e.start_date DESC;