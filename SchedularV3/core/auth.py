"""
JWT Authentication Utilities for SchedularV3

This module provides secure JWT token generation and validation utilities.
It demonstrates best practices for JWT authentication when the FastAPI 
backend is implemented.

IMPORTANT: This is a template module for future use. JWT authentication
is not currently implemented in SchedularV3.

Security Features:
- Environment variable-based secret key (never hardcoded)
- Fail-fast validation at startup
- Secure token generation with expiration
- Token validation with proper error handling
- Type hints for better code safety

Usage Example:
    >>> from config.settings import validate_jwt_config
    >>> from core.auth import create_access_token, verify_token
    >>> 
    >>> # Validate configuration at startup
    >>> validate_jwt_config()
    >>> 
    >>> # Create a token
    >>> token = create_access_token({"sub": "user123"})
    >>> 
    >>> # Verify a token
    >>> payload = verify_token(token)
    >>> print(payload["sub"])  # "user123"

Requirements:
    When implementing JWT authentication, add these dependencies:
    - python-jose[cryptography] or PyJWT
    - python-dotenv (optional, for .env file support)
    - passlib[bcrypt] (for password hashing)
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
import warnings

# Note: These imports will fail if dependencies are not installed
# This is intentional - it will remind developers to install required packages
try:
    from jose import jwt, JWTError
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    warnings.warn(
        "python-jose not installed. JWT authentication is not available. "
        "To enable JWT: pip install python-jose[cryptography]",
        category=ImportWarning
    )

from config.settings import (
    SECRET_KEY,
    JWT_ALGORITHM,
    JWT_EXPIRATION_MINUTES,
    validate_jwt_config
)


class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass


class TokenExpiredError(AuthenticationError):
    """Raised when a token has expired."""
    pass


class TokenInvalidError(AuthenticationError):
    """Raised when a token is invalid."""
    pass


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.
    
    This function generates a JWT token with the provided data and an
    expiration time. The token is signed using the SECRET_KEY from
    environment variables.
    
    Args:
        data: Dictionary of claims to include in the token
        expires_delta: Optional custom expiration time. If not provided,
                      uses JWT_EXPIRATION_MINUTES from settings
    
    Returns:
        str: Encoded JWT token
        
    Raises:
        ValueError: If SECRET_KEY is not configured
        RuntimeError: If python-jose is not installed
        
    Example:
        >>> token = create_access_token({"sub": "user123", "role": "student"})
        >>> print(token)  # eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    """
    if not JWT_AVAILABLE:
        raise RuntimeError(
            "JWT library not available. Install python-jose: "
            "pip install python-jose[cryptography]"
        )
    
    # Validate configuration before proceeding
    validate_jwt_config()
    
    # Create a copy to avoid modifying the original data
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRATION_MINUTES)
    
    # Add expiration and issued-at claims
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc)
    })
    
    # Encode the token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify and decode a JWT token.
    
    This function validates the token signature, checks expiration,
    and returns the decoded payload.
    
    Args:
        token: The JWT token to verify
        
    Returns:
        Dict[str, Any]: Decoded token payload
        
    Raises:
        TokenExpiredError: If the token has expired
        TokenInvalidError: If the token is invalid or signature doesn't match
        ValueError: If SECRET_KEY is not configured
        RuntimeError: If python-jose is not installed
        
    Example:
        >>> token = create_access_token({"sub": "user123"})
        >>> payload = verify_token(token)
        >>> print(payload["sub"])  # "user123"
    """
    if not JWT_AVAILABLE:
        raise RuntimeError(
            "JWT library not available. Install python-jose: "
            "pip install python-jose[cryptography]"
        )
    
    # Validate configuration before proceeding
    validate_jwt_config()
    
    try:
        # Decode and verify the token
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )
        return payload
        
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError("Token has expired")
        
    except JWTError as e:
        raise TokenInvalidError(f"Invalid token: {str(e)}")


def get_user_from_token(token: str) -> Optional[str]:
    """
    Extract user identifier from token.
    
    This is a convenience function that extracts the 'sub' (subject)
    claim from a token, which typically contains the user identifier.
    
    Args:
        token: The JWT token
        
    Returns:
        Optional[str]: User identifier if present, None otherwise
        
    Raises:
        TokenExpiredError: If the token has expired
        TokenInvalidError: If the token is invalid
        
    Example:
        >>> token = create_access_token({"sub": "user123"})
        >>> user_id = get_user_from_token(token)
        >>> print(user_id)  # "user123"
    """
    payload = verify_token(token)
    return payload.get("sub")


# =============================================================================
# FastAPI Integration Example (for future implementation)
# =============================================================================

"""
When implementing FastAPI backend with JWT authentication:

1. Install dependencies:
   pip install fastapi uvicorn python-jose[cryptography] passlib[bcrypt] python-dotenv

2. Set up .env file with SECRET_KEY (see .env.example)

3. Example FastAPI implementation:

```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from core.auth import verify_token, create_access_token, TokenInvalidError

app = FastAPI()
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthCredentials = Depends(security)
) -> dict:
    '''Dependency to get current authenticated user.'''
    try:
        token = credentials.credentials
        payload = verify_token(token)
        return payload
    except TokenInvalidError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.post("/login")
async def login(username: str, password: str):
    '''Login endpoint - returns JWT token.'''
    # TODO: Verify username/password against database
    # For now, this is just an example
    user_id = "user123"
    token = create_access_token({"sub": user_id, "username": username})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/protected")
async def protected_route(user: dict = Depends(get_current_user)):
    '''Protected endpoint - requires valid JWT token.'''
    return {"message": f"Hello {user.get('username', 'user')}!"}
```

4. Startup validation (in main.py or app startup):

```python
from config.settings import validate_jwt_config

@app.on_event("startup")
async def startup_event():
    '''Validate configuration at startup.'''
    try:
        validate_jwt_config()
        print("✓ JWT configuration validated")
    except ValueError as e:
        print(f"✗ JWT configuration error: {e}")
        raise
```

5. Testing:

```bash
# Start the server
uvicorn main:app --reload

# Login to get token
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}'

# Use token to access protected endpoint
curl "http://localhost:8000/protected" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```
"""
