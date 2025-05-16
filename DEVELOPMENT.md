# LibraryHub Development Guide

This guide explains how to run LibraryHub in both local development and GitHub Codespaces environments.

## Development Environments

LibraryHub supports two development environments:

1. **Local Development**: Uses your local MySQL database
2. **Codespace Development**: Uses the container-based MySQL database in GitHub Codespaces

## Local Development Setup

### Prerequisites
- Python 3.6+
- MySQL installed locally
- The MySQL root password should be set to `12345678` (or you can modify `init_local_db.py` to match your setup)

### Setup Steps

1. **Initialize the Local Database**:
   ```
   python init_local_db.py
   ```
   This creates the `libraryhub` database, all required tables, and sample data.

2. **Run the Application (Local Mode)**:
   ```
   python run_local.py
   ```
   This launches the app using your local MySQL database.

3. **Access the Application**:
   Open your browser and go to:
   ```
   http://localhost:5000
   ```

4. **Login with Default Credentials**:
   - Username: `admin`
   - Password: `admin123`
   - **Important**: Change this password after first login!

## GitHub Codespaces Setup

### Prerequisites
- GitHub account with access to the repository
- Access to GitHub Codespaces

### Setup Steps

1. **Create a Codespace**:
   - Go to the GitHub repository
   - Click the "Code" button
   - Select the "Codespaces" tab
   - Click "Create codespace on main"

2. **Run the Application (Codespace Mode)**:
   Once the Codespace is ready, run:
   ```
   python run_codespace.py
   ```
   This launches the app using the container MySQL database.

3. **Access the Application**:
   - Look for the "Ports" tab at the bottom of the VS Code interface
   - Find port 5000 and click "Open in Browser"

4. **Login with Default Credentials**:
   - Username: `admin`
   - Password: `admin123`
   - **Important**: Change this password after first login!

## Troubleshooting

### Local Database Connection Issues
If you encounter database connection problems when running locally:

1. Verify MySQL is running:
   ```
   mysqladmin -u root -p ping
   ```

2. Check your MySQL credentials match those in `init_local_db.py`

3. Try manually initializing the database:
   ```
   mysql -u root -p
   ```
   Then run:
   ```
   CREATE DATABASE IF NOT EXISTS libraryhub;
   ```

### Codespace Database Connection Issues
If you encounter database connection problems in Codespaces:

1. Verify the containers are running:
   ```
   docker ps
   ```
   You should see both the app and db containers running.

2. Try manually initializing the database:
   ```
   python codespace_db_init.py
   ```

3. Check the logs for the MySQL container:
   ```
   docker logs $(docker ps -q --filter name=db)
   ```

## Switching Between Environments

The application detects which environment to use based on the `USE_CODESPACE_DB` environment variable:

- If `USE_CODESPACE_DB=true`, it uses the Codespace configuration
- Otherwise, it uses the local configuration

The launcher scripts (`run_local.py` and `run_codespace.py`) set this variable automatically. 