#!/usr/bin/env python3
"""
Codespace development launcher for LibraryHub
This script ensures the application uses the Docker container MySQL database.
"""

import os
import sys
import subprocess

# Make sure we're using the container database configuration
os.environ['USE_CODESPACE_DB'] = 'true'

print("==============================================")
print("🚀 Starting LibraryHub in CODESPACE mode")
print("📊 Using CONTAINER MySQL database configuration:")
print("    Host: db")
print("    User: library_user")
print("    Database: librarydb")
print("==============================================")

try:
    # Execute the main application
    result = subprocess.run([sys.executable, "app.py"])
    sys.exit(result.returncode)
except KeyboardInterrupt:
    print("\nApplication stopped by user")
    sys.exit(0)
except Exception as e:
    print(f"Error running the application: {e}")
    sys.exit(1) 