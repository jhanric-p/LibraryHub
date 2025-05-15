import mysql.connector
import bcrypt


def init_db(db_config_param, get_db_connection_func):
    """Initializes the database schema if tables don't exist."""
    conn = None
    try:
        # Connect without specifying a database to create it if it doesn't exist
        temp_conn_details = db_config_param.copy()
        db_name = temp_conn_details.pop('database')
        
        if not mysql.connector:
            print("mysql.connector is not available in db_initialization.py")
            return

        conn_no_db = mysql.connector.connect(**temp_conn_details)
        cursor_no_db = conn_no_db.cursor()
        cursor_no_db.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        cursor_no_db.close()
        conn_no_db.close()
        print(f"Database '{db_name}' ensured by db_initialization.")

        # Now connect to the specific database using the passed function
        conn = get_db_connection_func()
        if not conn:
            print("Failed to connect to the database after ensuring its existence (from db_initialization).")
            return

        cursor = conn.cursor()
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                role ENUM('user', 'admin') NOT NULL DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Books table
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
        # Borrowings table
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
        print("Database tables ensured by db_initialization.")

        
        cursor.execute("SELECT id FROM users WHERE username = %s AND role = %s", ('admin', 'admin'))
        if not cursor.fetchone():
            admin_pass = 'admin123' # Default admin password
            hashed_admin_pass = bcrypt.hashpw(admin_pass.encode('utf-8'), bcrypt.gensalt())
            cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                           ('admin', hashed_admin_pass.decode('utf-8'), 'admin'))
            conn.commit()
            print(f"Default admin user 'admin' created by db_initialization with password '{admin_pass}'. PLEASE CHANGE THIS PASSWORD.")
        cursor.close()

    except mysql.connector.Error as err:
        print(f"Error during DB initialization (in db_initialization.py): {err}")
    except Exception as e:
        print(f"An unexpected error occurred in init_db: {e}")
    finally:
        if conn and conn.is_connected():
            conn.close()

if __name__ == '__main__':

    print("db_initialization.py run directly - defining local DB_CONFIG and get_db_connection for setup.")
    

    LOCAL_DB_CONFIG = {
        'host': 'db',
        'user': 'library_user', 
        'password': 'library_password', 
        'database': 'librarydb' 
    }

    def local_get_db_connection():
        try:
            return mysql.connector.connect(**LOCAL_DB_CONFIG)
        except mysql.connector.Error as err:
            print(f"Local DB connection error (standalone db_initialization): {err}")
            return None
            
    init_db(LOCAL_DB_CONFIG, local_get_db_connection)
