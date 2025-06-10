"""
Authentication Manager for Esoteric AI Agent

Simple, secure authentication system with:
- Username/password authentication
- Secure password hashing (PBKDF2)
- User session isolation
- File-based user storage
- Integration with existing session management
"""

import hashlib
import json
import os
import secrets
import time
from pathlib import Path
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from contextlib import contextmanager

from utils.logger import logger


@dataclass
class User:
    """User account data class."""
    username: str
    password_hash: str
    salt: str
    created_at: float
    last_login: float
    is_active: bool = True
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'User':
        """Create User from dictionary."""
        return cls(**data)


class AuthenticationManager:
    """
    Simple authentication manager for CLI application.
    
    Features:
    - Secure password hashing with PBKDF2-SHA256
    - User registration and login
    - Session isolation per user
    - File-based user storage
    - Integration with existing session system
    """
    
    def __init__(self, users_file: str = "data/auth/users.json"):
        """Initialize authentication manager."""
        self.users_file = Path(users_file)
        self.current_user: Optional[User] = None
        self._users_cache: Dict[str, User] = {}
        
        # Ensure auth directory exists
        self.users_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing users
        self._load_users()
    
    def _load_users(self) -> None:
        """Load users from file."""
        try:
            if self.users_file.exists():
                with open(self.users_file, 'r') as f:
                    users_data = json.load(f)
                    self._users_cache = {
                        username: User.from_dict(user_data)
                        for username, user_data in users_data.items()
                    }
            else:
                self._users_cache = {}
                logger.debug("No users file found, starting with empty user base")
        except Exception as e:
            logger.error(f"Failed to load users: {e}")
            self._users_cache = {}
    
    def _save_users(self) -> None:
        """Save users to file."""
        try:
            users_data = {
                username: user.to_dict()
                for username, user in self._users_cache.items()
            }
            
            # Atomic write using temporary file
            temp_file = self.users_file.with_suffix('.tmp')
            with open(temp_file, 'w') as f:
                json.dump(users_data, f, indent=2)
            
            # Replace original file atomically
            temp_file.replace(self.users_file)
            
        except Exception as e:
            logger.error(f"Failed to save users: {e}")
            raise
    
    def _hash_password(self, password: str, salt: str) -> str:
        """Hash password using PBKDF2-SHA256."""
        # Use PBKDF2 with 100,000 iterations for security
        password_bytes = password.encode('utf-8')
        salt_bytes = salt.encode('utf-8')
        
        # PBKDF2-HMAC-SHA256 with 100k iterations
        hash_bytes = hashlib.pbkdf2_hmac('sha256', password_bytes, salt_bytes, 100000)
        return hash_bytes.hex()
    
    def _generate_salt(self) -> str:
        """Generate a random salt for password hashing."""
        return secrets.token_hex(32)
    
    def _verify_password(self, password: str, hash_str: str, salt: str) -> bool:
        """Verify password against stored hash."""
        return self._hash_password(password, salt) == hash_str
    
    def register_user(self, username: str, password: str) -> Tuple[bool, str]:
        """
        Register a new user.
        
        Args:
            username: Username (must be unique)
            password: Plain text password
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Validate input
            if not username or not username.strip():
                return False, "Username cannot be empty"
            
            if len(username.strip()) < 3:
                return False, "Username must be at least 3 characters"
            
            if not password or len(password) < 6:
                return False, "Password must be at least 6 characters"
            
            username = username.strip().lower()
            
            # Check if user already exists
            if username in self._users_cache:
                return False, f"User '{username}' already exists"
            
            # Create new user
            salt = self._generate_salt()
            password_hash = self._hash_password(password, salt)
            
            user = User(
                username=username,
                password_hash=password_hash,
                salt=salt,
                created_at=time.time(),
                last_login=0.0,
                is_active=True
            )
            
            # Add to cache and save
            self._users_cache[username] = user
            self._save_users()
            
            logger.user_registered(username)
            return True, f"User '{username}' registered successfully"
            
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return False, f"Registration failed: {e}"
    
    def login(self, username: str, password: str) -> Tuple[bool, str]:
        """
        Authenticate user login.
        
        Args:
            username: Username
            password: Plain text password
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            if not username or not password:
                return False, "Username and password required"
            
            username = username.strip().lower()
            
            # Check if user exists
            if username not in self._users_cache:
                return False, "Invalid username or password"
            
            user = self._users_cache[username]
            
            # Check if user is active
            if not user.is_active:
                return False, "Account is disabled"
            
            # Verify password
            if not self._verify_password(password, user.password_hash, user.salt):
                return False, "Invalid username or password"
            
            # Update last login
            user.last_login = time.time()
            self._save_users()
            
            # Set current user
            self.current_user = user
            
            logger.user_login(username)
            return True, f"Welcome back, {username}!"
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False, f"Login failed: {e}"
    
    def logout(self) -> None:
        """Logout current user."""
        if self.current_user:
            logger.user_logout(self.current_user.username)
            self.current_user = None
    
    def is_authenticated(self) -> bool:
        """Check if a user is currently authenticated."""
        return self.current_user is not None
    
    def get_current_user(self) -> Optional[User]:
        """Get currently authenticated user."""
        return self.current_user
    
    def get_current_username(self) -> Optional[str]:
        """Get current username or None if not authenticated."""
        return self.current_user.username if self.current_user else None
    
    def get_user_session_path(self, base_path: str = "data/sessions") -> str:
        """
        Get user-specific session storage path.
        
        Args:
            base_path: Base sessions directory
            
        Returns:
            User-specific session path
        """
        if not self.current_user:
            raise ValueError("No user authenticated")
        
        # Create user-specific subdirectory
        user_path = Path(base_path) / f"user_{self.current_user.username}"
        user_path.mkdir(parents=True, exist_ok=True)
        
        return str(user_path / "graph_checkpoints.db")
    
    def list_users(self) -> Dict[str, Dict]:
        """
        List all users (admin function).
        
        Returns:
            Dictionary of usernames and their public info
        """
        return {
            username: {
                "username": user.username,
                "created_at": user.created_at,
                "last_login": user.last_login,
                "is_active": user.is_active
            }
            for username, user in self._users_cache.items()
        }
    
    def delete_user(self, username: str) -> Tuple[bool, str]:
        """
        Delete a user account.
        
        Args:
            username: Username to delete
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            username = username.strip().lower()
            
            if username not in self._users_cache:
                return False, f"User '{username}' not found"
            
            # Prevent deleting currently logged in user
            if self.current_user and self.current_user.username == username:
                return False, "Cannot delete currently logged in user"
            
            # Remove user
            del self._users_cache[username]
            self._save_users()
            
            # Also remove user's session directory
            user_session_dir = Path("data/sessions") / f"user_{username}"
            if user_session_dir.exists():
                import shutil
                shutil.rmtree(user_session_dir)
            
            logger.user_deleted(username)
            return True, f"User '{username}' deleted successfully"
            
        except Exception as e:
            logger.error(f"User deletion error: {e}")
            return False, f"Deletion failed: {e}"
    
    @contextmanager
    def require_auth(self):
        """Context manager that requires authentication."""
        if not self.is_authenticated():
            raise ValueError("Authentication required")
        yield self.current_user 