#!/usr/bin/env python3
"""
Specialized version of the LibraryHub app for Codespaces environment.
This version imports configuration from the auto-generated config_codespace.py file.
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import mysql.connector
import bcrypt
import os
from functools import wraps
from datetime import datetime, timedelta
import sys

# Check if config_codespace.py exists
if not os.path.exists('config_codespace.py'):
    print("❌ config_codespace.py not found! Please run direct_mysql_setup.py first.")
    print("   Run: python direct_mysql_setup.py")
    sys.exit(1)

# Import database configuration from the auto-generated file
try:
    from config_codespace import DB_CONFIG
    print("✅ Successfully imported database configuration from config_codespace.py")
except ImportError:
    print("❌ Failed to import configuration from config_codespace.py")
    print("   Please run direct_mysql_setup.py to generate the configuration")
    sys.exit(1)

# --- Application Setup ---
app = Flask(__name__)
app.secret_key = 'a_very_secret_and_static_key_for_development'  # Static secret key for development

@app.context_processor
def inject_current_year():
    return {'current_year': datetime.now().year}

# --- Database Configuration is imported from config_codespace.py ---

def get_db_connection():
    """Establishes a connection to the MySQL database."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        flash(f"Error connecting to database: {err}", "danger")
        print(f"Error connecting to database: {err}")
        return None

# --- Login Manager Setup ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect to login page if user is not authenticated

class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    if not conn:
        return None
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, username, role FROM users WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    conn.close()
    if user_data:
        return User(user_data['id'], user_data['username'], user_data['role'])
    return None

# --- Decorators ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash("You do not have permission to access this page.", "danger")
            return redirect(url_for('user_dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# --- Routes ---

# --- Authentication Routes ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        conn = get_db_connection()
        if not conn:
            return render_template('register.html', error="Database connection failed.")
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                           (username, hashed_password.decode('utf-8'), 'user')) # Default role is 'user'
            conn.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            flash(f'Error: {err}', 'danger')
        finally:
            cursor.close()
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('user_dashboard')) # Corrected redirect
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        if not conn:
            return render_template('login.html', error="Database connection failed.")
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()

        if user_data and bcrypt.checkpw(password.encode('utf-8'), user_data['password'].encode('utf-8')):
            user = User(user_data['id'], user_data['username'], user_data['role'])
            login_user(user)
            flash('Login successful!', 'success')
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# --- Main Routes ---
@app.route('/')
@login_required
def user_dashboard():
    conn = get_db_connection()
    if not conn:
        # flash("Database connection failed.", "danger") # Already handled by get_db_connection
        return render_template('user/user_dashboard.html', stats={}, recently_borrowed=[])

    cursor = conn.cursor(dictionary=True)
    user_id = current_user.id
    stats = {}
    recently_borrowed = []
    today = datetime.now().date() # Use date object for comparisons with due_date if it's just a date

    try:
        # Count of books currently borrowed by the user
        cursor.execute("""
            SELECT COUNT(*) as count FROM borrowings
            WHERE user_id = %s AND return_date IS NULL
        """, (user_id,))
        stats['borrowed_books_count'] = cursor.fetchone()['count']

        # Count of overdue books for the user
        cursor.execute("""
            SELECT COUNT(*) as count FROM borrowings
            WHERE user_id = %s AND return_date IS NULL AND due_date < CURDATE()
        """, (user_id,))
        stats['overdue_books_count'] = cursor.fetchone()['count']
        
        # Total available books in the library
        cursor.execute("SELECT SUM(available_copies) as count FROM books WHERE available_copies > 0")
        total_available = cursor.fetchone()
        stats['total_available_books'] = total_available['count'] if total_available and total_available['count'] else 0
        
        # Recently borrowed books by the user (e.g., last 5, including returned)
        cursor.execute("""
            SELECT b.title, bor.borrow_date, bor.due_date, bor.return_date, bor.book_id,
                   (bor.return_date IS NULL AND bor.due_date < CURDATE()) as is_overdue
            FROM borrowings bor
            JOIN books b ON bor.book_id = b.id
            WHERE bor.user_id = %s
            ORDER BY bor.borrow_date DESC
            LIMIT 5
        """, (user_id,))
        recently_borrowed = cursor.fetchall()

    except mysql.connector.Error as err:
        flash(f"Error fetching dashboard data: {err}", "danger")
    finally:
        cursor.close()
        conn.close()
        
    return render_template('user/user_dashboard.html', stats=stats, recently_borrowed=recently_borrowed, today=today)

@app.route('/available_books')
@login_required
def available_books():
    conn = get_db_connection()
    if not conn:
        return render_template('available_books.html', books=[], error="Database connection failed.")
    cursor = conn.cursor(dictionary=True)
    # Fetch all available books
    cursor.execute("SELECT id, title, author, isbn, available_copies FROM books WHERE available_copies > 0 ORDER BY title")
    books_data = cursor.fetchall() # Renamed to avoid conflict
    cursor.close()
    conn.close()
    return render_template('available_books.html', books=books_data)

# Include the rest of your existing routes...
# For brevity, I'm not including all routes here,
# but they would be copied from app.py

# --- Main Execution ---
if __name__ == '__main__':
    print("🚀 Starting LibraryHub with Codespace-specific configuration...")
    app.run(debug=True, host="0.0.0.0", port=5000) 