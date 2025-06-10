#!/usr/bin/env python3
"""
Startup script for Esoteric AI Agent Web API
"""

import os
import sys
import subprocess

def start_api():
    """Start the web API server"""
    print("🌙 Esoteric AI Agent - Web API Startup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("src/web_api.py"):
        print("❌ Error: web_api.py not found in src/ directory")
        print("   Please run this script from the project root directory")
        return False
    
    # Add src directory to Python path instead of changing directory
    src_path = os.path.abspath("src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    print("🚀 Starting FastAPI server...")
    print("📖 API Documentation will be available at: http://localhost:8000/docs")
    print("🔄 Health Check: http://localhost:8000/health")
    print("💬 Chat Endpoint: POST http://localhost:8000/chat")
    print("🌙 Lunar Info: GET http://localhost:8000/lunar")
    print()
    print("Press Ctrl+C to stop the server")
    print()
    
    try:
        # Start the server from project root (not src/)
        subprocess.run([
            sys.executable, "-m", "uvicorn", "src.web_api:app", 
            "--host", "0.0.0.0", "--port", "8000", "--reload"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False
    
    return True

if __name__ == "__main__":
    start_api() 