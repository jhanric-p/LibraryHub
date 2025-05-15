#!/usr/bin/env python3
"""
Specialized database initialization script for codespaces environment.
This script directly uses the container-specific database settings and
works around potential issues with localhost connections.
"""

import mysql.connector
import time
import sys
import bcrypt

# Container-specific database configuration
CODESPACE_DB_CONFIG = {
    'host': 'db',
    'user': 'library_user',
    'password': 'library_password',
    'database': 'librarydb'
}

def wait_for_db():
    """Wait for the database to become available."""
    max_attempts = 10
    attempt = 0
    while attempt < max_attempts:
        try:
            # Try to connect without specifying a database
            temp_config = CODESPACE_DB_CONFIG.copy()
            db_name = temp_config.pop('database')
            
            conn = mysql.connector.connect(**temp_config)
            conn.close()
            print("Database server is available!")
            return True
        except mysql.connector.Error as err:
            attempt += 1
            if attempt < max_attempts:
                print(f"Waiting for database to be ready... ({attempt}/{max_attempts})")
                time.sleep(3)  # Wait 3 seconds before retrying
            else:
                print(f"Could not connect to database after {max_attempts} attempts: {err}")
                return False

def init_codespace_db():
    """Initialize the database for codespaces environment."""
    if not wait_for_db():
        print("Failed to connect to database. Exiting.")
        sys.exit(1)
        
    conn = None
    try:
        # Create database if it doesn't exist
        temp_config = CODESPACE_DB_CONFIG.copy()
        db_name = temp_config.pop('database')
        
        conn_no_db = mysql.connector.connect(**temp_config)
        cursor_no_db = conn_no_db.cursor()
        cursor_no_db.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        cursor_no_db.close()
        conn_no_db.close()
        print(f"Database '{db_name}' created or already exists.")
        
        # Connect to the database
        conn = mysql.connector.connect(**CODESPACE_DB_CONFIG)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                role ENUM('user', 'admin') NOT NULL DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                author VARCHAR(255) NOT NULL,
                isbn VARCHAR(20) UNIQUE NOT NULL,
                total_copies INT DEFAULT 1,
                available_copies INT DEFAULT 1,
                description TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS borrowings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                book_id INT NOT NULL,
                borrow_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                due_date TIMESTAMP NOT NULL,
                return_date TIMESTAMP NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE RESTRICT
            )
        """)
        
        conn.commit()
        print("Database tables created successfully!")
        
        # Create default admin user if it doesn't exist
        cursor.execute("SELECT id FROM users WHERE username = 'admin' AND role = 'admin'")
        if not cursor.fetchone():
            admin_pass = 'admin123'
            hashed_admin_pass = bcrypt.hashpw(admin_pass.encode('utf-8'), bcrypt.gensalt())
            cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                          ('admin', hashed_admin_pass.decode('utf-8'), 'admin'))
            conn.commit()
            print(f"Default admin user created: username='admin', password='{admin_pass}'")
            print("IMPORTANT: Please change this password after first login!")
        
        # Add sample books if none exist
        cursor.execute("SELECT COUNT(*) FROM books")
        if cursor.fetchone()[0] == 0:
            sample_books = [
                ('The Great Gatsby', 'F. Scott Fitzgerald', '9780743273565', 5, 5, 
                 'A novel about the American Dream and its corruption'),
                ('To Kill a Mockingbird', 'Harper Lee', '9780061120084', 3, 3, 
                 'Classic novel about racial injustice in the American South'),
                ('1984', 'George Orwell', '9780451524935', 4, 4, 
                 'Dystopian novel about totalitarianism and surveillance')
            ]
            
            for book in sample_books:
                cursor.execute("""
                    INSERT INTO books (title, author, isbn, total_copies, available_copies, description)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, book)
            
            conn.commit()
            print("Sample books added to the database.")
        
    except mysql.connector.Error as err:
        print(f"Error during database initialization: {err}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    print("Starting codespace database initialization...")
    init_codespace_db()
    print("Database initialization complete!") 