-- LibraryHub Database Schema
-- This file contains all necessary SQL to create the database and required tables

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS librarydb;
USE librarydb;

-- Create Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('user', 'admin') NOT NULL DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Books table
CREATE TABLE IF NOT EXISTS books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    isbn VARCHAR(20) UNIQUE NOT NULL,
    total_copies INT DEFAULT 1,
    available_copies INT DEFAULT 1,
    description TEXT,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Borrowings table
CREATE TABLE IF NOT EXISTS borrowings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    book_id INT NOT NULL,
    borrow_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    due_date TIMESTAMP NOT NULL,
    return_date TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE RESTRICT
);

-- Create default admin user with password 'admin123'
-- Note: In production, you should change this password immediately
INSERT INTO users (username, password, role) 
VALUES ('admin', '$2b$12$7y3vKmgRRQ3Y9UvxKYS./.4W.FYxGUZlxVNLLZJYo1xFQY8TxF8Si', 'admin')
ON DUPLICATE KEY UPDATE id=id;

-- Optional: Insert some sample books
INSERT INTO books (title, author, isbn, total_copies, available_copies, description)
VALUES 
('The Great Gatsby', 'F. Scott Fitzgerald', '9780743273565', 5, 5, 'A novel about the American Dream and its corruption'),
('To Kill a Mockingbird', 'Harper Lee', '9780061120084', 3, 3, 'Classic novel about racial injustice in the American South'),
('1984', 'George Orwell', '9780451524935', 4, 4, 'Dystopian novel about totalitarianism and surveillance')
ON DUPLICATE KEY UPDATE id=id; 