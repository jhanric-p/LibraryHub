#!/usr/bin/env python3
"""
Local development launcher for LibraryHub
This script ensures the application uses your local MySQL database.
"""

import os
import sys
import subprocess

# Make sure we're using the local database configuration
os.environ['USE_CODESPACE_DB'] = 'false'

print("==============================================")
print("🚀 Starting LibraryHub in LOCAL mode")
print("📊 Using LOCAL MySQL database configuration:")
print("    Host: localhost")
print("    User: root")
print("    Database: libraryhub")
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