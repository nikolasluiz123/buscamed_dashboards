INSERT INTO sync_control (execution_type, last_sync_date)
VALUES (?, ?) ON CONFLICT (execution_type) DO
UPDATE SET last_sync_date = excluded.last_sync_date;