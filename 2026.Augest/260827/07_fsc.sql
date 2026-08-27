CREATE DATABASE IF NOT EXISTS fsc_db 
    DEFAULT CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

USE fsc_db;

CREATE TABLE raw_item(
    raw_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    url    TEXT,
    collected_at  DATETIME NOT NULL,
    payload LONGTEXT NOT NULL,
    content_hash CHAR(64) NOT NULL,

    UNIQUE KEY uq_hash (content_hash),
    KEY idx_source_date(source, collected_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;