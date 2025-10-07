CREATE TABLE IF NOT EXISTS tgdb_log (
    id SERIAL PRIMARY KEY,
    datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id VARCHAR(32),
    username VARCHAR(32),
    action VARCHAR(32),
    message VARCHAR(256)
);