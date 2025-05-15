from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import mysql.connector
import bcrypt
import os
from functools import wraps
from datetime import datetime, timedelta

# --- Application Setup ---
app = Flask(__name__)
app.secret_key = 'a_very_secret_and_static_key_for_development'  # Static secret key for development

@app.context_processor
def inject_current_year():
    return {'current_year': datetime.now().year}

# --- Database Configuration ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '12345678',
    'database': 'libraryhub'
}

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

# --- Book Management Routes (User-facing) ---
@app.route('/book/<int:book_id>')
@login_required
def book_details(book_id):
    conn = get_db_connection()
    if not conn:
        flash("Database connection failed.", "danger")
        return redirect(url_for('available_books')) # Redirect to book list on DB error
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM books WHERE id = %s", (book_id,))
    book = cursor.fetchone()
    cursor.close()
    conn.close()
    if book:
        return render_template('user/book_details.html', book=book)
    flash("Book not found.", "warning")
    return redirect(url_for('available_books')) # Redirect to book list if book not found

# --- Borrowing System Routes ---
@app.route('/borrow/<int:book_id>', methods=['POST'])
@login_required
def borrow_book(book_id):
    conn = get_db_connection()
    if not conn:
        flash("Database connection failed.", "danger")
        return redirect(url_for('book_details', book_id=book_id))

    cursor = conn.cursor(dictionary=True)
    try:
        # Check if book is available
        cursor.execute("SELECT available_copies FROM books WHERE id = %s", (book_id,))
        book = cursor.fetchone()
        if book and book['available_copies'] > 0:
            # Check if user already borrowed this book and not returned
            cursor.execute("""
                SELECT * FROM borrowings
                WHERE user_id = %s AND book_id = %s AND return_date IS NULL
            """, (current_user.id, book_id))
            existing_borrowing = cursor.fetchone()
            if existing_borrowing:
                flash("You have already borrowed this book and not returned it.", "warning")
                return redirect(url_for('book_details', book_id=book_id))

            # Record borrowing
            due_date = datetime.now() + timedelta(days=14) # Example: 2 weeks due date
            cursor.execute("""
                INSERT INTO borrowings (user_id, book_id, borrow_date, due_date)
                VALUES (%s, %s, NOW(), %s)
            """, (current_user.id, book_id, due_date))
            # Decrement available copies
            cursor.execute("UPDATE books SET available_copies = available_copies - 1 WHERE id = %s", (book_id,))
            conn.commit()
            flash("Book borrowed successfully!", "success")
        else:
            flash("Book is not available or does not exist.", "warning")
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f"Error borrowing book: {err}", "danger")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('book_details', book_id=book_id))

@app.route('/return_book/<int:borrowing_id>', methods=['POST'])
@login_required
def return_book(borrowing_id):
    conn = get_db_connection()
    if not conn:
        flash("Database connection failed.", "danger")
        return redirect(url_for('borrowing_history'))

    cursor = conn.cursor()
    try:
        # Get book_id from borrowing record
        cursor.execute("SELECT book_id FROM borrowings WHERE id = %s AND user_id = %s AND return_date IS NULL",
                       (borrowing_id, current_user.id))
        borrowing_data = cursor.fetchone()

        if borrowing_data:
            book_id = borrowing_data[0]
            # Mark as returned
            cursor.execute("UPDATE borrowings SET return_date = NOW() WHERE id = %s", (borrowing_id,))
            # Increment available copies
            cursor.execute("UPDATE books SET available_copies = available_copies + 1 WHERE id = %s", (book_id,))
            conn.commit()
            flash("Book returned successfully!", "success")
        else:
            flash("Borrowing record not found or book already returned.", "warning")
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f"Error returning book: {err}", "danger")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('borrowing_history'))

@app.route('/borrowing_history')
@login_required
def borrowing_history():
    conn = get_db_connection()
    if not conn:
        return render_template('borrowing_history.html', borrowings=[], error="Database connection failed.")
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT b.title, bor.borrow_date, bor.due_date, bor.return_date, bor.id as borrowing_id
        FROM borrowings bor
        JOIN books b ON bor.book_id = b.id
        WHERE bor.user_id = %s
        ORDER BY bor.borrow_date DESC
    """, (current_user.id,))
    borrowings = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('borrowing_history.html', borrowings=borrowings)

@app.route('/meet_the_devs')
def meet_the_devs():
    return render_template('devs/meet_the_devs.html')

@app.route('/dev/pablo')
def dev_pablo():
    return render_template('devs/pablo.html')

@app.route('/dev/paulite')
def dev_paulite():
    return render_template('devs/paulite.html')

@app.route('/dev/cruz')
def dev_cruz():
    return render_template('devs/cruz.html')

@app.route('/dev/habitan')
def dev_habitan():
    return render_template('devs/habitan.html')

# --- Admin Dashboard Routes ---
@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    conn = get_db_connection()
    if not conn:
        return render_template('admin/dashboard.html', stats={}, error="Database connection failed.")
    cursor = conn.cursor(dictionary=True)
    # Fetch stats
    cursor.execute("SELECT COUNT(*) as total_books FROM books")
    total_books = cursor.fetchone()['total_books']
    cursor.execute("SELECT COUNT(*) as total_users FROM users")
    total_users = cursor.fetchone()['total_users']
    cursor.execute("SELECT COUNT(*) as borrowed_books FROM borrowings WHERE return_date IS NULL")
    borrowed_books = cursor.fetchone()['borrowed_books']
    stats = {
        'total_books': total_books,
        'total_users': total_users,
        'borrowed_books': borrowed_books
    }
    cursor.close()
    conn.close()
    return render_template('admin/dashboard.html', stats=stats)

# --- Admin Book Management ---
@app.route('/admin/books')
@login_required
@admin_required
def admin_manage_books():
    conn = get_db_connection()
    if not conn:
        return render_template('admin/manage_books.html', books=[], error="Database connection failed.")
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM books ORDER BY title")
    books = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('admin/manage_books.html', books=books)

@app.route('/admin/book/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        isbn = request.form['isbn']
        total_copies = request.form.get('total_copies', type=int)
        available_copies = request.form.get('available_copies', type=int, default=total_copies) # Default to total_copies if not provided
        description = request.form.get('description', '')

        conn = get_db_connection()
        if not conn:
            return render_template('admin/add_edit_book.html', action="Add", error="Database connection failed.")
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO books (title, author, isbn, total_copies, available_copies, description)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (title, author, isbn, total_copies, available_copies, description))
            conn.commit()
            flash("Book added successfully!", "success")
            return redirect(url_for('admin_manage_books'))
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error adding book: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
    return render_template('admin/add_edit_book.html', action="Add", book={})


@app.route('/admin/book/edit/<int:book_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_book(book_id):
    conn = get_db_connection()
    if not conn:
        flash("Database connection failed.", "danger")
        return redirect(url_for('admin_manage_books'))
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        isbn_val = request.form['isbn'] # Renamed to avoid conflict with isbnlib
        total_copies = request.form.get('total_copies', type=int)
        available_copies = request.form.get('available_copies', type=int)
        description = request.form.get('description', '')

        try:
            cursor.execute("""
                UPDATE books SET title = %s, author = %s, isbn = %s,
                               total_copies = %s, available_copies = %s, description = %s
                WHERE id = %s
            """, (title, author, isbn_val, total_copies, available_copies, description, book_id))
            conn.commit()
            flash("Book updated successfully!", "success")
            return redirect(url_for('admin_manage_books'))
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error updating book: {err}", "danger")
        finally:
            cursor.close()
            conn.close() # Close connection in finally block

    # GET request: fetch book details
    cursor.execute("SELECT * FROM books WHERE id = %s", (book_id,))
    book = cursor.fetchone()
    cursor.close()
    conn.close() # Close connection after fetching
    if book:
        return render_template('admin/add_edit_book.html', action="Edit", book=book)
    flash("Book not found.", "warning")
    return redirect(url_for('admin_manage_books'))

@app.route('/admin/book/delete/<int:book_id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_book(book_id):
    conn = get_db_connection()
    if not conn:
        flash("Database connection failed.", "danger")
        return redirect(url_for('admin_manage_books'))
    cursor = conn.cursor()
    try:
        # Check for active borrowings before deleting
        cursor.execute("SELECT COUNT(*) FROM borrowings WHERE book_id = %s AND return_date IS NULL", (book_id,))
        active_borrowings = cursor.fetchone()[0]
        if active_borrowings > 0:
            flash("Cannot delete book. It has active borrowings.", "danger")
            return redirect(url_for('admin_manage_books'))

        cursor.execute("DELETE FROM books WHERE id = %s", (book_id,))
        conn.commit()
        flash("Book deleted successfully!", "success")
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f"Error deleting book: {err}", "danger")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('admin_manage_books'))

# --- Admin User Management ---
@app.route('/admin/users')
@login_required
@admin_required
def admin_manage_users():
    conn = get_db_connection()
    if not conn:
        return render_template('admin/manage_users.html', users=[], error="Database connection failed.")
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, username, role, created_at FROM users ORDER BY username")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('admin/manage_users.html', users=users)

@app.route('/admin/user/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_user(user_id):
    conn = get_db_connection()
    if not conn:
        flash("Database connection failed.", "danger")
        return redirect(url_for('admin_manage_users'))
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        username = request.form['username']
        role = request.form['role']
        password = request.form.get('password') # Optional: only update if provided

        try:
            if password:
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                cursor.execute("UPDATE users SET username = %s, role = %s, password = %s WHERE id = %s",
                               (username, role, hashed_password.decode('utf-8'), user_id))
            else:
                cursor.execute("UPDATE users SET username = %s, role = %s WHERE id = %s",
                               (username, role, user_id))
            conn.commit()
            flash("User updated successfully!", "success")
            return redirect(url_for('admin_manage_users'))
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error updating user: {err}", "danger")
        finally:
            cursor.close()
            conn.close() # Close connection in finally block

    # GET request: fetch user details
    cursor.execute("SELECT id, username, role FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close() # Close connection after fetching
    if user:
        return render_template('admin/edit_user.html', user=user)
    flash("User not found.", "warning")
    return redirect(url_for('admin_manage_users'))


@app.route('/admin/user/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_user(user_id):
    if user_id == current_user.id: # Prevent admin from deleting themselves
        flash("You cannot delete your own account.", "danger")
        return redirect(url_for('admin_manage_users'))

    conn = get_db_connection()
    if not conn:
        flash("Database connection failed.", "danger")
        return redirect(url_for('admin_manage_users'))
    cursor = conn.cursor()
    try:
        # Check for active borrowings by this user
        cursor.execute("SELECT COUNT(*) FROM borrowings WHERE user_id = %s AND return_date IS NULL", (user_id,))
        active_borrowings = cursor.fetchone()[0]
        if active_borrowings > 0:
            flash("Cannot delete user. They have active borrowings.", "danger")
            return redirect(url_for('admin_manage_users'))

        # Optional: Reassign or delete related records (e.g., borrowings history)
        # For simplicity, we'll just delete the user if no active borrowings.
        # Consider cascading deletes or soft deletes in a real application.
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        flash("User deleted successfully!", "success")
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f"Error deleting user: {err}", "danger")
    finally:
        if conn and conn.is_connected():
            conn.close()
    return redirect(url_for('admin_manage_users'))

# --- Main Execution ---
if __name__ == '__main__':
    from db_initialization import init_db # Changed to direct import
    # DB_CONFIG and get_db_connection are defined at the top level of this file (app.py)
    init_db(DB_CONFIG, get_db_connection) # Initialize database schema on startup
    app.run(debug=True)
