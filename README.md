# LibraryHub

A simple library management system built with Flask that allows for book borrowing, user management, and administrator functions.

## Setup Instructions

### Prerequisites
- Python 3.7+
- MySQL database (MySQL Server 5.7+ recommended)
- pip (Python package installer)

### Required Python Packages
- Flask (2.0+)
- mysql-connector-python (8.0+)
- bcrypt (3.2+)
- Flask-Login (0.6+)

### Installation Steps

1. **Clone the repository**

2. **Set up a virtual environment (recommended)**
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install required packages**
   ```
   pip install -r requirements.txt
   ```

4. **Configure database connection**
   
   Edit the `DB_CONFIG` in `app.py` if needed:
   ```python
   DB_CONFIG = {
       'host': 'localhost',
       'user': 'root',
       'password': '12345678',
       'database': 'libraryhub'
   }
   ```

5. **Create and populate the database**
   ```
   mysql -u root -p < schema.sql
   ```
   
   Enter your MySQL password when prompted. This will:
   - Create the libraryhub database
   - Set up all required tables
   - Create a default admin user (username: admin, password: admin123)
   - Add some sample books

6. **Start the application**
   ```
   python app.py
   ```

7. **Access the application**
   
   Open your browser and navigate to:
   ```
   http://localhost:5000/
   ```

### Default Login Credentials
- Admin User: 
  - Username: admin
  - Password: admin123
  - **IMPORTANT**: Change this password after first login!

## Features

- User Registration and Authentication
- Book borrowing and returning
- Admin dashboard for managing books and users
- User dashboard to track borrowing history

## Meet the Developers

The "Meet the Devs" section showcases the team that developed this application. Visit `/meet_the_devs` to learn more about the developers. # LibraryHub
