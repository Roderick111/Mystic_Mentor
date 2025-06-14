#!/usr/bin/env python3
"""
HTTPS Startup script for Esoteric AI Agent Web API
Runs the backend API on HTTPS to eliminate mixed content security errors
"""

import os
import sys
import subprocess
from pathlib import Path

def create_self_signed_cert():
    """Create a self-signed certificate for localhost if it doesn't exist"""
    cert_file = "ssl/localhost.pem"
    key_file = "ssl/localhost-key.pem"
    
    if Path(cert_file).exists() and Path(key_file).exists():
        print("✅ SSL certificates already exist")
        return cert_file, key_file
    
    try:
        print("🔐 Creating self-signed certificate for localhost...")
        
        # Generate private key
        subprocess.run([
            'openssl', 'genrsa', '-out', key_file, '2048'
        ], check=True, capture_output=True)
        
        # Generate certificate
        subprocess.run([
            'openssl', 'req', '-new', '-x509', '-key', key_file, '-out', cert_file, '-days', '365',
            '-subj', '/C=US/ST=CA/L=Local/O=Dev/CN=localhost'
        ], check=True, capture_output=True)
        
        print("✅ SSL certificate created successfully")
        return cert_file, key_file
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create certificate: {e}")
        print("💡 Make sure OpenSSL is installed: brew install openssl")
        return None, None
    except FileNotFoundError:
        print("❌ OpenSSL not found. Please install it: brew install openssl")
        return None, None

def start_api_https():
    """Start the web API server with HTTPS"""
    print("🌙 Esoteric AI Agent - HTTPS Web API Startup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("src/web_api.py"):
        print("❌ Error: web_api.py not found in src/ directory")
        print("   Please run this script from the project root directory")
        return False
    
    # Create SSL certificates
    cert_file, key_file = create_self_signed_cert()
    if not cert_file or not key_file:
        print("❌ Cannot start HTTPS server without SSL certificates")
        return False
    
    # Add src directory to Python path
    src_path = os.path.abspath("src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    print("🚀 Starting FastAPI server with HTTPS...")
    print("📖 API Documentation: https://localhost:8001/docs")
    print("🔄 Health Check: https://localhost:8001/health")
    print("💬 Chat Endpoint: POST https://localhost:8001/chat")
    print("🌙 Lunar Info: GET https://localhost:8001/lunar")
    print("💳 Stripe Config: GET https://localhost:8001/stripe/config")
    print()
    print("⚠️  You'll need to accept the self-signed certificate warning")
    print("🔐 This eliminates HTTPS/HTTP mixed content security errors")
    print()
    print("Press Ctrl+C to stop the server")
    print()
    
    try:
        # Start the server with HTTPS
        subprocess.run([
            sys.executable, "-m", "uvicorn", "src.web_api:app", 
            "--host", "0.0.0.0", "--port", "8001", "--reload",
            "--ssl-keyfile", key_file,
            "--ssl-certfile", cert_file
        ])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False
    
    return True

if __name__ == "__main__":
    start_api_https() 