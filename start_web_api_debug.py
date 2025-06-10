#!/usr/bin/env python3
"""
Debug startup script for Esoteric AI Agent Web API
Automatically enables debug mode for full logging visibility
"""

import os
import sys

# Set debug mode environment variable
os.environ["DEBUG_MODE"] = "true"

# Import and run the main startup function
from start_web_api import start_api

if __name__ == "__main__":
    print("🐛 Debug Mode Startup Script")
    print("📝 Full logging notifications will be enabled")
    print()
    start_api() 