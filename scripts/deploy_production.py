#!/usr/bin/env python3
"""
Production Deployment Script for Esoteric Vectors

Helps set up and verify production-ready deployment with Auth0 authentication.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_environment():
    """Check if all required environment variables are set."""
    print("🔍 Checking environment configuration...")
    
    required_vars = [
        'AUTH0_DOMAIN',
        'AUTH0_AUDIENCE', 
        'GOOGLE_API_KEY',
    ]
    
    optional_vars = [
        'OPENAI_API_KEY',
        'PRODUCTION_MODE',
        'API_HOST',
        'API_PORT',
        'ALLOWED_ORIGINS',
    ]
    
    missing_required = []
    missing_optional = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)
        else:
            print(f"✅ {var}: {os.getenv(var)[:20]}...")
    
    for var in optional_vars:
        if not os.getenv(var):
            missing_optional.append(var)
        else:
            print(f"✅ {var}: {os.getenv(var)}")
    
    if missing_required:
        print(f"\n❌ Missing required environment variables: {', '.join(missing_required)}")
        print("📝 Create a .env file with these variables or set them in your environment")
        return False
    
    if missing_optional:
        print(f"\n⚠️ Missing optional environment variables: {', '.join(missing_optional)}")
        print("💡 These can be set for enhanced functionality")
    
    return True

def check_dependencies():
    """Check if all dependencies are installed."""
    print("\n📦 Checking dependencies...")
    
    try:
        import authlib
        import httpx
        from jose import jwt
        print("✅ Auth0 dependencies installed")
    except ImportError as e:
        print(f"❌ Missing Auth0 dependencies: {e}")
        print("🔧 Run: uv sync")
        return False
    
    try:
        import fastapi
        import uvicorn
        print("✅ FastAPI dependencies installed")
    except ImportError as e:
        print(f"❌ Missing FastAPI dependencies: {e}")
        return False
    
    return True

def check_auth0_integration():
    """Run Auth0 integration tests."""
    print("\n🧪 Running Auth0 integration tests...")
    
    try:
        result = subprocess.run([
            sys.executable, 'test_auth0.py'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Auth0 integration tests passed")
            return True
        else:
            print("❌ Auth0 integration tests failed:")
            print(result.stdout)
            print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("❌ Auth0 tests timed out")
        return False
    except Exception as e:
        print(f"❌ Failed to run Auth0 tests: {e}")
        return False

def check_directory_structure():
    """Check if required directories exist."""
    print("\n📁 Checking directory structure...")
    
    required_dirs = [
        'data/sessions',
        'data/chroma_db',
        'src/core',
        'docs',
        'config',
    ]
    
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"✅ {dir_path}")
        else:
            print(f"❌ Missing directory: {dir_path}")
            try:
                path.mkdir(parents=True, exist_ok=True)
                print(f"   Created: {dir_path}")
            except Exception as e:
                print(f"   Failed to create: {e}")
                return False
    
    return True

def check_auth0_setup():
    """Verify Auth0 is properly configured."""
    print("\n🔐 Verifying Auth0 setup...")
    
    domain = os.getenv('AUTH0_DOMAIN')
    audience = os.getenv('AUTH0_AUDIENCE')
    
    if not domain or not audience:
        print("❌ Auth0 not configured (AUTH0_DOMAIN or AUTH0_AUDIENCE missing)")
        return False
    
    # Basic validation
    if not domain.endswith('.auth0.com'):
        print(f"⚠️ AUTH0_DOMAIN should end with '.auth0.com': {domain}")
    
    if not audience.startswith('http'):
        print(f"⚠️ AUTH0_AUDIENCE should be a URL (API identifier): {audience}")
    
    print(f"✅ Auth0 Domain: {domain}")
    print(f"✅ Auth0 Audience: {audience}")
    
    return True

def start_production_server():
    """Start the production server."""
    print("\n🚀 Starting production server...")
    
    # Set production environment
    os.environ['PRODUCTION_MODE'] = 'true'
    
    host = os.getenv('API_HOST', '0.0.0.0')
    port = int(os.getenv('API_PORT', '8000'))
    
    print(f"🌐 Server will start on {host}:{port}")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔄 Health Check: http://localhost:8000/health")
    print("🔐 Auth Status: http://localhost:8000/auth/status")
    
    try:
        import uvicorn
        uvicorn.run(
            "src.web_api:app",
            host=host,
            port=port,
            reload=False,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        return False
    
    return True

def main():
    """Main deployment script."""
    print("🎯 Esoteric Vectors - Production Deployment")
    print("=" * 50)
    
    # Check if running from project root
    if not os.path.exists('src/web_api.py'):
        print("❌ Please run this script from the project root directory")
        return False
    
    # Run all checks
    checks = [
        check_directory_structure,
        check_dependencies,
        check_environment,
        check_auth0_setup,
        check_auth0_integration,
    ]
    
    print("🔍 Running pre-deployment checks...")
    
    for check in checks:
        if not check():
            print(f"\n❌ Deployment check failed: {check.__name__}")
            print("🔧 Please fix the issues above before deploying to production")
            return False
    
    print("\n" + "=" * 50)
    print("✅ All deployment checks passed!")
    print("🎉 Ready for production deployment")
    
    # Ask if user wants to start server
    try:
        response = input("\n🚀 Start production server now? (y/N): ").strip().lower()
        if response in ['y', 'yes']:
            return start_production_server()
        else:
            print("\n📝 To start manually:")
            print("   python src/web_api.py")
            print("\n📚 Setup documentation:")
            print("   docs/AUTH0_SETUP.md")
            return True
    except KeyboardInterrupt:
        print("\n👋 Deployment cancelled by user")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 