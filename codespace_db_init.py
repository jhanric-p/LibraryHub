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
import os

# Container-specific database configuration
CODESPACE_DB_CONFIG = {
    'host': 'db',
    'user': 'library_user',
    'password': 'library_password',
    'database': 'librarydb'
}

def wait_for_db():
    """Wait for the database to become available."""
    print("Checking database connectivity...")
    max_attempts = 15  # Increased attempts
    attempt = 0
    while attempt < max_attempts:
        try:
            # Try to connect without specifying a database
            temp_config = CODESPACE_DB_CONFIG.copy()
            db_name = temp_config.pop('database')
            
            print(f"Attempt {attempt+1}/{max_attempts}: Connecting to MySQL at {temp_config['host']}...")
            conn = mysql.connector.connect(**temp_config)
            conn.close()
            print("✅ Database server is available!")
            return True
        except mysql.connector.Error as err:
            attempt += 1
            if attempt < max_attempts:
                print(f"⏳ Waiting for database to be ready... ({attempt}/{max_attempts})")
                print(f"   Error: {err}")
                if "Unknown MySQL server host" in str(err):
                    print("   It looks like the database container might not be running or reachable.")
                    print("   Make sure the Docker containers are running correctly.")
                    # Try to connect to localhost just to see if MySQL is available at all
                    try:
                        alt_config = temp_config.copy()
                        alt_config['host'] = 'localhost'
                        print("   Trying localhost connection as fallback...")
                        local_conn = mysql.connector.connect(**alt_config)
                        local_conn.close()
                        print("   ✅ MySQL is available on localhost but not on 'db' hostname.")
                        print("   This suggests the Docker container networking might not be set up correctly.")
                    except:
                        pass
                time.sleep(3)  # Wait 3 seconds before retrying
            else:
                print(f"❌ Could not connect to database after {max_attempts} attempts: {err}")
                print("\nPossible issues and solutions:")
                print("1. The MySQL container might not be running.")
                print("   Run 'docker ps' to check if the 'db' container is running.")
                print("2. There might be a network configuration issue.")
                print("   Make sure your docker-compose.yml has the correct service names.")
                print("3. The MySQL service might need more time to initialize.")
                print("   Try running this script again after a minute.")
                return False

def init_codespace_db():
    """Initialize the database for codespaces environment."""
    print("Starting Codespace database initialization...")
    
    if not wait_for_db():
        print("Failed to connect to database. Exiting.")
        return False
        
    conn = None
    try:
        # Create database if it doesn't exist
        temp_config = CODESPACE_DB_CONFIG.copy()
        db_name = temp_config.pop('database')
        
        print(f"Creating database '{db_name}' if it doesn't exist...")
        conn_no_db = mysql.connector.connect(**temp_config)
        cursor_no_db = conn_no_db.cursor()
        cursor_no_db.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        cursor_no_db.close()
        conn_no_db.close()
        print(f"✅ Database '{db_name}' created or already exists.")
        
        # Connect to the database
        print(f"Connecting to database '{db_name}'...")
        conn = mysql.connector.connect(**CODESPACE_DB_CONFIG)
        cursor = conn.cursor()
        
        # Create tables
        print("Creating database tables...")
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
        print("✅ Database tables created successfully!")
        
        # Create default admin user if it doesn't exist
        print("Checking for admin user...")
        cursor.execute("SELECT id FROM users WHERE username = 'admin' AND role = 'admin'")
        if not cursor.fetchone():
            print("Creating default admin user...")
            admin_pass = 'admin123'
            hashed_admin_pass = bcrypt.hashpw(admin_pass.encode('utf-8'), bcrypt.gensalt())
            cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                          ('admin', hashed_admin_pass.decode('utf-8'), 'admin'))
            conn.commit()
            print(f"✅ Default admin user created: username='admin', password='{admin_pass}'")
            print("   IMPORTANT: Please change this password after first login!")
        else:
            print("✅ Admin user already exists.")
        
        # Add sample books if none exist
        print("Checking for sample books...")
        cursor.execute("SELECT COUNT(*) FROM books")
        if cursor.fetchone()[0] == 0:
            print("Adding sample books...")
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
            print("✅ Sample books added to the database.")
        else:
            print("✅ Sample books already exist.")
        
    except mysql.connector.Error as err:
        print(f"❌ Error during database initialization: {err}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
            print("Database connection closed.")
    
    return True

if __name__ == "__main__":
    print("==============================================")
    print("📊 CODESPACE DATABASE INITIALIZATION")
    print("    Host: db (MySQL container)")
    print("    User: library_user")
    print("    Database: librarydb")
    print("==============================================")
    
    if init_codespace_db():
        print("\n✅ Codespace database initialization completed successfully!")
    else:
        print("\n❌ Codespace database initialization failed.")
        print("\nTROUBLESHOOTING SUGGESTIONS:")
        print("1. Check if the MySQL container is running:")
        print("   docker ps | grep db")
        print("2. Check Docker container logs:")
        print("   docker logs $(docker ps -q --filter name=db)")
        print("3. Verify docker-compose.yml has the correct service setup")
        print("4. Try rebuilding the containers:")
        print("   - Click the Dev Container button in the bottom-left corner")
        print("   - Select 'Rebuild Container'")
        sys.exit(1) 