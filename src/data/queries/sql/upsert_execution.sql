INSERT INTO executions (id, execution_type, processing_type, input_text, input_tokens, output_tokens, result,
                        success, start_date, end_date, storage_image_path, prompt, client_processor_version)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT (id) DO
UPDATE SET
    result = excluded.result,
    success = excluded.success,
    prompt = excluded.prompt,
    client_processor_version = excluded.client_processor_version;