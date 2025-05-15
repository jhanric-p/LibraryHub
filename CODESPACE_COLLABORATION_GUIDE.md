# GitHub Codespaces Collaboration Guide for LibraryHub

This guide is specifically for team members who have been invited to collaborate on the LibraryHub project through a shared GitHub Codespace. Follow these steps to get started and contribute effectively.

## Getting Started with the Shared Codespace

### 1. Access the Shared Codespace

1. **Check your email** for an invitation to the GitHub repository or Codespace
2. **Accept the invitation** by clicking on the link provided
3. **Sign in to GitHub** if you haven't already

### 2. Opening the Codespace

1. **Navigate to the repository** on GitHub
2. **Click on the "Code" button** (green button)
3. **Select the "Codespaces" tab**
4. **Click on the existing Codespace** that has been shared with you
   - Alternatively, you might see a notification with a direct link to the Codespace

### 3. Familiarize Yourself with the Environment

The Codespace is a fully configured development environment in the cloud that includes:
- Visual Studio Code (or similar editor) in your browser
- All necessary extensions pre-installed
- The complete LibraryHub codebase
- Required dependencies already installed
- Development server ready to run

## Working with the Codebase

### 1. Understanding the Project Structure

The LibraryHub project has the following key components:
- `app.py`: Main Flask application file
- `schema.sql`: Database schema definition
- `templates/`: HTML templates for the application
- `static/`: CSS, JavaScript, and other static assets
- `requirements.txt`: Python dependencies

### 2. Running the Application Locally in the Codespace

1. **Open a terminal** in the Codespace (Terminal > New Terminal)
2. **Activate the virtual environment** (if not already activated):
   ```
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Run the Flask application**:
   ```
   python app.py
   ```
4. **Access the application** by clicking on the "Open in Browser" button or the provided URL

### 3. Making Changes

1. **Create a new branch** before making changes:
   ```
   git checkout -b feature/your-feature-name
   ```
2. **Make your code changes** using the editor
3. **Test your changes** by running the application
4. **Commit your changes**:
   ```
   git add .
   git commit -m "Description of changes"
   ```
5. **Push your branch** to the repository:
   ```
   git push -u origin feature/your-feature-name
   ```

### 4. Creating Pull Requests

1. **Go to the repository** on GitHub
2. **Click on "Pull requests"** tab
3. **Click "New pull request"**
4. **Select your branch** as the compare branch
5. **Add a title and description** explaining your changes
6. **Click "Create pull request"**

## Database Setup and Management

### 1. Setting Up the Database in Your Codespace

The Codespace may already have the database set up. If not:

1. **Check if MySQL is running**:
   ```
   sudo service mysql status
   ```
2. **Start MySQL if needed**:
   ```
   sudo service mysql start
   ```
3. **Create the database and tables**:
   ```
   mysql -u root -p < schema.sql
   ```
   (Use the MySQL password from the README or provided by the team)

### 2. Accessing the Database

1. **Connect to MySQL**:
   ```
   mysql -u root -p
   ```
2. **Select the database**:
   ```
   USE libraryhub;
   ```
3. **Run queries** as needed

## Collaboration Best Practices

### 1. Communication

- **Check for existing issues** before starting work
- **Assign yourself to issues** you're working on
- **Comment on pull requests** with feedback
- **Use GitHub Discussions** for longer conversations

### 2. Code Quality

- **Follow the existing code style** (indentation, naming conventions, etc.)
- **Add meaningful comments** to explain complex logic
- **Write clear commit messages** that explain the "why" not just the "what"
- **Keep pull requests focused** on a single feature or fix

### 3. Testing

- **Test your changes thoroughly** before submitting a pull request
- **Check for edge cases** and potential errors
- **Verify that existing functionality** still works correctly

### 4. Handling Conflicts

1. **Pull the latest changes** from the main branch regularly:
   ```
   git checkout main
   git pull
   git checkout your-branch
   git merge main
   ```
2. **Resolve any merge conflicts** that arise
3. **Test again** after resolving conflicts

## Common Issues and Solutions

### 1. Codespace Connection Issues

- **Refresh the browser** if the Codespace becomes unresponsive
- **Restart the Codespace** from the GitHub interface if needed
- **Check your internet connection**

### 2. Database Connection Issues

- **Verify the DB_CONFIG settings** in app.py
- **Check if MySQL is running** in the Codespace
- **Reset the database** if tables become corrupted:
  ```
  mysql -u root -p < schema.sql
  ```

### 3. Git Issues

- **Discard local changes** if needed:
  ```
  git checkout -- filename
  ```
- **Stash changes temporarily**:
  ```
  git stash
  # Do something else
  git stash pop  # To restore the changes
  ```

## Getting Help

If you encounter issues not covered in this guide:

1. **Check GitHub Issues** for similar problems and solutions
2. **Ask team members** in GitHub Discussions or your team's communication channel
3. **Document solutions** you find for others to reference 