INSERT INTO executions (id, execution_type, input_tokens, output_tokens, result,
                        success, start_date, end_date, storage_image_path, prompt)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT (id) DO
UPDATE SET
    result = excluded.result,
    success = excluded.success,
    prompt = excluded.prompt;