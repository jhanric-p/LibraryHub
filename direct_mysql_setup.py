#!/usr/bin/env python3
"""
Direct MySQL setup script to address persistent connection issues in Codespaces.
This script tries multiple connection methods to establish a database connection.
"""

import mysql.connector
import time
import sys
import os
import bcrypt
import subprocess

print("🔍 Direct MySQL setup script starting...")

# Try multiple potential connection configurations
CONNECTIONS_TO_TRY = [
    {
        'name': 'Container connection via "db" hostname',
        'config': {
            'host': 'db',
            'user': 'root',
            'password': 'librarydb',  # From docker-compose.yml MYSQL_ROOT_PASSWORD
            'port': 3306
        }
    },
    {
        'name': 'Container connection via localhost',
        'config': {
            'host': '127.0.0.1',
            'user': 'root',
            'password': 'librarydb',  # From docker-compose.yml MYSQL_ROOT_PASSWORD
            'port': 3306
        }
    },
    {
        'name': 'Container connection via app user',
        'config': {
            'host': 'db',
            'user': 'library_user',
            'password': 'library_password',  # From docker-compose.yml
            'port': 3306
        }
    }
]

# Get Docker container status
print("📊 Checking Docker containers...")
try:
    result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
    print(result.stdout)
    
    if 'mysql' not in result.stdout.lower():
        print("⚠️ Warning: MySQL container may not be running!")
except Exception as e:
    print(f"Error checking Docker status: {e}")

# Database name
DB_NAME = 'librarydb'

# Try each connection configuration
successful_config = None

for conn_option in CONNECTIONS_TO_TRY:
    print(f"\n🔄 Trying {conn_option['name']}...")
    
    # Try multiple attempts for each configuration
    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        try:
            print(f"  Attempt {attempt}/{max_attempts}...")
            conn = mysql.connector.connect(**conn_option['config'])
            print(f"✅ Success! Connected with {conn_option['name']}")
            successful_config = conn_option['config']
            conn.close()
            break
        except mysql.connector.Error as err:
            print(f"  ❌ Connection failed: {err}")
            time.sleep(2)
    
    if successful_config:
        break

if not successful_config:
    print("❌ All connection attempts failed. Trying manual MySQL CLI approach...")
    try:
        # Try using the mysql CLI client directly
        mysql_cmd = f"mysql -h db -u root -p'librarydb' -e 'SHOW DATABASES;'"
        print(f"Running: {mysql_cmd}")
        result = subprocess.run(mysql_cmd, shell=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(f"Error: {result.stderr}")
        # If we get here without exception, the CLI worked
        print("MySQL CLI connection succeeded. Will use CLI for database setup.")
        # Set up database via CLI
        setup_commands = [
            f"CREATE DATABASE IF NOT EXISTS {DB_NAME};",
            f"USE {DB_NAME};",
            "DROP USER IF EXISTS 'library_user'@'%';",
            "CREATE USER 'library_user'@'%' IDENTIFIED BY 'library_password';",
            f"GRANT ALL PRIVILEGES ON {DB_NAME}.* TO 'library_user'@'%';",
            "FLUSH PRIVILEGES;"
        ]
        combined_cmd = " ".join(setup_commands)
        mysql_cmd = f"mysql -h db -u root -p'librarydb' -e \"{combined_cmd}\""
        print(f"Running setup commands...")
        subprocess.run(mysql_cmd, shell=True)
        print("✅ Database and user setup via CLI completed.")
        
        # Now create a new app config file that uses these credentials
        with open('config_codespace.py', 'w') as f:
            f.write("""# Auto-generated Codespace configuration
DB_CONFIG = {
    'host': 'db',
    'user': 'library_user',
    'password': 'library_password',
    'database': 'librarydb'
}
""")
        print("✅ Created config_codespace.py with working credentials")
        sys.exit(0)
    except Exception as e:
        print(f"❌ MySQL CLI approach failed: {e}")
        sys.exit(1)

# If we get here, we have a working connection configuration
print(f"\n✅ Found working connection: {successful_config}")

# Create database
try:
    print(f"\n🔄 Creating database {DB_NAME}...")
    conn = mysql.connector.connect(**successful_config)
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    print(f"✅ Database {DB_NAME} created or already exists")
    
    # Create library_user if needed
    cursor.execute("SELECT User FROM mysql.user WHERE User = 'library_user'")
    if not cursor.fetchone():
        print("🔄 Creating library_user...")
        cursor.execute("CREATE USER 'library_user'@'%' IDENTIFIED BY 'library_password'")
        cursor.execute(f"GRANT ALL PRIVILEGES ON {DB_NAME}.* TO 'library_user'@'%'")
        cursor.execute("FLUSH PRIVILEGES")
        print("✅ User library_user created with appropriate permissions")
    else:
        print("✅ User library_user already exists")
    
    cursor.close()
    conn.close()
except mysql.connector.Error as err:
    print(f"❌ Error creating database: {err}")
    sys.exit(1)

# Now connect to the specific database and create tables
try:
    print(f"\n🔄 Setting up tables in {DB_NAME}...")
    db_config = successful_config.copy()
    db_config['database'] = DB_NAME
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(100) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        role ENUM('user', 'admin') NOT NULL DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Create books table
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
    
    # Create borrowings table
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
    
    print("✅ Tables created successfully")
    
    # Create default admin user
    cursor.execute("SELECT id FROM users WHERE username = 'admin' AND role = 'admin'")
    if not cursor.fetchone():
        print("🔄 Creating default admin user...")
        admin_pass = 'admin123'
        hashed_admin_pass = bcrypt.hashpw(admin_pass.encode('utf-8'), bcrypt.gensalt())
        cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                      ('admin', hashed_admin_pass.decode('utf-8'), 'admin'))
        conn.commit()
        print(f"✅ Default admin user created: username='admin', password='{admin_pass}'")
        print("⚠️ IMPORTANT: Please change this password after first login!")
    else:
        print("✅ Admin user already exists")
    
    # Add sample books if none exist
    cursor.execute("SELECT COUNT(*) FROM books")
    if cursor.fetchone()[0] == 0:
        print("🔄 Adding sample books...")
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
        print("✅ Sample books added to the database")
    
    cursor.close()
    conn.close()
    
    # Create a new app config file that uses these credentials
    with open('config_codespace.py', 'w') as f:
        f.write("""# Auto-generated Codespace configuration
DB_CONFIG = {
    'host': 'db',
    'user': 'library_user',
    'password': 'library_password',
    'database': 'librarydb'
}
""")
    print("✅ Created config_codespace.py with working credentials")
    
    print("\n✅ Database setup completed successfully!")
    print("➡️ Run your app with 'python app_codespace.py' to use these settings")
    
except mysql.connector.Error as err:
    print(f"❌ Error setting up database tables: {err}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1) 