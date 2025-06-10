#!/usr/bin/env python3
"""
Utility script to toggle authentication on/off in the Esoteric AI Agent.

Usage:
  python toggle_auth.py off    # Disable authentication (development)
  python toggle_auth.py on     # Enable authentication (production)
  python toggle_auth.py status # Show current status
"""

import sys

def get_current_auth_status():
    """Check if authentication is currently enabled or disabled."""
    try:
        with open('src/main.py', 'r') as f:
            content = f.read()
        
        # Look for the development mode indicator
        if "Development Mode: Authentication temporarily disabled" in content:
            return "DISABLED"
        elif "if not authenticate_user():" in content:
            return "ENABLED"
        else:
            return "UNKNOWN"
    except Exception as e:
        print(f"❌ Error reading main.py: {e}")
        return "ERROR"

def main():
    if len(sys.argv) != 2:
        print("🔧 Authentication Toggle Utility")
        print("Usage: python toggle_auth.py [status]")
        print()
        print("Commands:")
        print("  status  - Show current authentication status")
        print()
        print("Note: Authentication is currently manually configured in src/main.py")
        print("Look for the 'TEMPORARY: Skip authentication' comment to modify.")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "status":
        status = get_current_auth_status()
        print(f"🔍 Authentication Status: {status}")
        if status == "DISABLED":
            print("🔧 Development Mode: No login required")
            print("📝 To enable: Uncomment authentication code in src/main.py")
        elif status == "ENABLED":
            print("🔐 Production Mode: Login required")
            print("📝 To disable: Comment out authentication code in src/main.py")
        else:
            print("❓ Status unclear - check src/main.py manually")
    
    else:
        print("❌ Invalid command. Use: status")
        sys.exit(1)

if __name__ == "__main__":
    main() 