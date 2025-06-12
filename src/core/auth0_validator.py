"""
Auth0 JWT Validator for FastAPI

Production-ready Auth0 JWT validation based on Context7 best practices.
Supports FastAPI integration with proper error handling and user extraction.
"""

import json
import os
from typing import Dict, Any, Optional
from urllib.request import urlopen
from urllib.error import URLError

import httpx
from authlib.oauth2.rfc7523 import JWTBearerTokenValidator
from authlib.jose.rfc7517.jwk import JsonWebKey
from authlib.jose import jwt, JoseError
from fastapi import HTTPException, status
from pydantic import BaseModel

from utils.logger import logger


class Auth0User(BaseModel):
    """Auth0 user information extracted from JWT."""
    sub: str  # Auth0 user ID (subject)
    email: Optional[str] = None
    name: Optional[str] = None
    nickname: Optional[str] = None
    picture: Optional[str] = None
    email_verified: Optional[bool] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    
    # Custom claims for Esoteric Vectors
    memory_preferences: Optional[Dict[str, Any]] = {}
    active_domains: Optional[list] = []
    session_settings: Optional[Dict[str, Any]] = {}


class Auth0JWTBearerTokenValidator(JWTBearerTokenValidator):
    """
    Auth0 JWT Bearer Token Validator for production use.
    
    Features:
    - Automatic JWKS fetching and caching
    - Proper error handling
    - Custom claims support
    - FastAPI integration
    """
    
    def __init__(self, domain: str, audience: str):
        """
        Initialize Auth0 JWT validator.
        
        Args:
            domain: Auth0 domain (e.g., 'your-tenant.auth0.com')
            audience: API identifier from Auth0 dashboard
        """
        self.domain = domain
        self.audience = audience
        self.issuer = f"https://{domain}/"
        
        try:
            # Fetch JWKS from Auth0
            jsonurl = urlopen(f"{self.issuer}.well-known/jwks.json", timeout=10)
            jwks_data = json.loads(jsonurl.read())
            public_key = JsonWebKey.import_key_set(jwks_data)
            
            # Initialize parent validator
            super(Auth0JWTBearerTokenValidator, self).__init__(public_key)
            
            # Configure required claims
            self.claims_options = {
                "exp": {"essential": True},
                "aud": {"essential": True, "value": audience},
                "iss": {"essential": True, "value": self.issuer},
            }
            
            logger.debug(f"✅ Auth0 JWT validator initialized for domain: {domain}")
            
        except URLError as e:
            logger.error(f"❌ Failed to fetch JWKS from Auth0: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service unavailable"
            )
        except Exception as e:
            logger.error(f"❌ Failed to initialize Auth0 validator: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication configuration error"
            )


class Auth0TokenValidator:
    """
    Production Auth0 token validator with caching and error handling.
    """
    
    def __init__(self, domain: str, audience: str):
        self.domain = domain
        self.audience = audience
        self.issuer = f"https://{domain}/"
        self._jwks = None
        self._jwks_last_fetch = 0
        self._jwks_cache_duration = 3600  # 1 hour cache
        
    async def _fetch_jwks(self) -> Dict[str, Any]:
        """Fetch JWKS from Auth0 with caching."""
        import time
        
        # Check cache
        current_time = time.time()
        if self._jwks and (current_time - self._jwks_last_fetch) < self._jwks_cache_duration:
            return self._jwks
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.issuer}.well-known/jwks.json")
                response.raise_for_status()
                
                self._jwks = response.json()
                self._jwks_last_fetch = current_time
                
                logger.debug("🔄 JWKS cache refreshed")
                return self._jwks
                
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ HTTP error fetching JWKS: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service unavailable"
            )
        except httpx.TimeoutException:
            logger.error("❌ Timeout fetching JWKS from Auth0")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service timeout"
            )
        except Exception as e:
            logger.error(f"❌ Unexpected error fetching JWKS: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication error"
            )
    
    def _get_signing_key(self, jwks: Dict[str, Any], kid: str) -> str:
        """Extract signing key from JWKS."""
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                return JsonWebKey.import_key(key)
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to find appropriate signing key"
        )
    
    async def validate_token(self, token: str) -> Auth0User:
        """
        Validate JWT token and extract user information.
        
        Args:
            token: JWT token string
            
        Returns:
            Auth0User: Validated user information
            
        Raises:
            HTTPException: On validation failure
        """
        try:
            # Get unverified header to extract key ID
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get("kid")
            
            if not kid:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token missing key ID"
                )
            
            # Fetch JWKS and get signing key
            jwks = await self._fetch_jwks()
            signing_key = self._get_signing_key(jwks, kid)
            
            # Validate and decode token
            payload = jwt.decode(
                token,
                signing_key,
                claims_options={
                    "exp": {"essential": True},
                    "aud": {"essential": True, "value": self.audience},
                    "iss": {"essential": True, "value": self.issuer},
                }
            )
            
            # Extract user information
            user_data = {
                "sub": payload["sub"],
                "email": payload.get("email"),
                "name": payload.get("name"),
                "nickname": payload.get("nickname"),
                "picture": payload.get("picture"),
                "email_verified": payload.get("email_verified"),
                "given_name": payload.get("given_name"),
                "family_name": payload.get("family_name"),
            }
            
            # Extract custom claims for Esoteric Vectors
            custom_claims = payload.get("https://esoteric-agent.com/user_metadata", {})
            user_data.update({
                "memory_preferences": custom_claims.get("memory_preferences", {}),
                "active_domains": custom_claims.get("active_domains", []),
                "session_settings": custom_claims.get("session_settings", {}),
            })
            
            logger.debug(f"✅ Token validated for user: {user_data['sub']}")
            return Auth0User(**user_data)
            
        except JoseError as e:
            logger.warning(f"🔒 JWT validation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected token validation error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Token validation error"
            )


def get_auth0_config() -> tuple[str, str]:
    """
    Get Auth0 configuration from environment variables.
    
    Returns:
        tuple: (domain, audience)
        
    Raises:
        ValueError: If required environment variables are missing
    """
    domain = os.getenv("AUTH0_DOMAIN")
    audience = os.getenv("AUTH0_AUDIENCE")
    
    if not domain:
        raise ValueError(
            "AUTH0_DOMAIN environment variable is required. "
            "Set it to your Auth0 tenant domain (e.g., 'your-tenant.auth0.com')"
        )
    
    if not audience:
        raise ValueError(
            "AUTH0_AUDIENCE environment variable is required. "
            "Set it to your Auth0 API identifier from the Auth0 dashboard"
        )
    
    return domain, audience


# Global validator instance (initialized on first import)
try:
    _auth0_domain, _auth0_audience = get_auth0_config()
    auth0_validator = Auth0TokenValidator(_auth0_domain, _auth0_audience)
    logger.debug("🔐 Auth0 validator initialized successfully")
except ValueError as e:
    logger.warning(f"⚠️ Auth0 not configured: {e}")
    auth0_validator = None
except Exception as e:
    logger.error(f"❌ Failed to initialize Auth0 validator: {e}")
    auth0_validator = None 