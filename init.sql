-- 初始化数据库脚本
CREATE DATABASE IF NOT EXISTS english_learning CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE english_learning;

-- 学习内容表
CREATE TABLE IF NOT EXISTS learning_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    type ENUM('word', 'phrase', 'sentence') NOT NULL,
    english TEXT NOT NULL,
    chinese TEXT NOT NULL,
    pronunciation VARCHAR(200),
    example_en TEXT,
    example_zh TEXT,
    audio_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_type (type),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 学习记录表
CREATE TABLE IF NOT EXISTS learning_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item_id INT NOT NULL,
    learned_date DATE NOT NULL,
    review_count INT DEFAULT 0,
    correct_count INT DEFAULT 0,
    wrong_count INT DEFAULT 0,
    last_review TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (item_id) REFERENCES learning_items(id) ON DELETE CASCADE,
    INDEX idx_item_date (item_id, learned_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 复习内容表
CREATE TABLE IF NOT EXISTS review_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item_id INT NOT NULL,
    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (item_id) REFERENCES learning_items(id) ON DELETE CASCADE,
    INDEX idx_item_reviewed (item_id, reviewed)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;