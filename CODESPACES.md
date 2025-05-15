# Using LibraryHub with GitHub Codespaces

This document explains how to set up and use LibraryHub in a GitHub Codespaces environment.

## Setup

1. **Create a new Codespace**:
   - Go to your GitHub repository
   - Click the "Code" button
   - Select the "Codespaces" tab
   - Click "Create codespace on main"

2. **Wait for the environment to initialize**:
   - GitHub will automatically set up your development environment using the `.devcontainer` configuration
   - This includes starting both the Python development container and the MySQL database

3. **Database initialization**:
   - The database will be automatically set up with the credentials configured in the docker-compose.yml file
   - When the codespace starts, the `postCreateCommand` in devcontainer.json will install dependencies
   - The first time you run the application, it will initialize the database schema and create a default admin user

## Running the Application

1. In the Terminal, run:
   ```
   python app.py
   ```

2. Click on the "Ports" tab at the bottom of the VS Code interface
   - You should see port 5000 (Flask app) and 3306 (MySQL) forwarded
   - Click the "Open in Browser" icon next to port 5000 to view the application

3. Login with the default admin credentials:
   - Username: `admin`
   - Password: `admin123`
   - **Important**: Change this password immediately after first login!

## Development Tips

1. **Database Connection**:
   - The app is configured to connect to the MySQL container using the host name `db`
   - Connection parameters are set in the `DB_CONFIG` in app.py

2. **Persistent Data**:
   - MySQL data is stored in a Docker volume, which persists across Codespace restarts
   - However, if you delete and recreate the Codespace, you'll start with a fresh database

3. **Debugging**:
   - VS Code's Python debugging tools are pre-installed
   - Set breakpoints in your code by clicking in the gutter (left margin)
   - Start debugging with F5 or the Run/Debug panel

## Troubleshooting

1. **Database Connection Issues**:
   - If you encounter database connection problems, ensure the MySQL container is running:
     ```
     docker ps
     ```
   - You should see two containers running (app and db)

2. **Port Forwarding**:
   - If you can't access the application, check the "Ports" tab to ensure port 5000 is forwarded

3. **Restarting Containers**:
   - You can rebuild the dev container by clicking on the "Dev Container" button in the bottom-left corner
   - Select "Rebuild Container" from the menu 