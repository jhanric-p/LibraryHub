#!/usr/bin/env python3
"""
Codespace development launcher for LibraryHub
This script ensures the application uses the Docker container MySQL database.
"""

import os
import sys
import subprocess
import time

# Make sure we're using the container database configuration
os.environ['USE_CODESPACE_DB'] = 'true'

print("==============================================")
print("🚀 Starting LibraryHub in CODESPACE mode")
print("📊 Using CONTAINER MySQL database configuration:")
print("    Host: db")
print("    User: library_user")
print("    Database: librarydb")
print("==============================================")

# Check if database service is running
try:
    print("Checking if MySQL service is available...")
    # First initialize the database to make sure it's ready
    print("Initializing database first...")
    db_init_result = subprocess.run([sys.executable, "codespace_db_init.py"], 
                                    capture_output=True, text=True)
    if db_init_result.returncode != 0:
        print("⚠️  Warning: Database initialization may have failed.")
        print(f"Error output: {db_init_result.stderr}")
        print("Will try to continue anyway...")
    else:
        print("✅ Database initialization completed")
        
    print("\n==============================================")
    print("Starting Flask application with the following settings:")
    print("- Binding to: 0.0.0.0 (all interfaces)")
    print("- Debug mode: enabled")
    print("- Port: 5000")
    print("==============================================")
    
    # Run the Flask app directly instead of using subprocess
    print("⏳ Starting the application... Please wait...")
    
    # Set Flask environment variables for better debugging
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = '1'
    
    # Import and run the Flask app directly
    print("Importing app.py...")
    from app import app
    print("Starting the Flask server...")
    app.run(debug=True, host="0.0.0.0", port=5000)
except KeyboardInterrupt:
    print("\nApplication stopped by user")
    sys.exit(0)
except Exception as e:
    print(f"❌ Error running the application: {e}")
    print("\nTROUBLESHOOTING TIPS:")
    print("1. Check if other services are using port 5000:")
    print("   lsof -i :5000")
    print("2. Make sure Docker containers are running:")
    print("   docker ps")
    print("3. Try running the app directly:")
    print("   export USE_CODESPACE_DB=true && python app.py")
    sys.exit(1) 