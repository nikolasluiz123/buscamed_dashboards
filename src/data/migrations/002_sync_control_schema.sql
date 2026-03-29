CREATE TABLE IF NOT EXISTS sync_control
(
    execution_type VARCHAR PRIMARY KEY,
    last_sync_date TIMESTAMP NOT NULL
);