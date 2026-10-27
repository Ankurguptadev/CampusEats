
-- 1. Create and select the database
CREATE DATABASE IF NOT EXISTS library;
USE library;

-- 2. Create the authors and books tables
-- WARNING: These DROP statements delete existing table data.
DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS authors;

CREATE TABLE authors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    country VARCHAR(50) DEFAULT NULL
);

CREATE TABLE books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    year INT DEFAULT NULL,
    author_id INT NOT NULL,
    CONSTRAINT fk_books_author
        FOREIGN KEY (author_id)
        REFERENCES authors(id)
);
