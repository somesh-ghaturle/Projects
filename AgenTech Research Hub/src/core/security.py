"""
Simple security utilities
"""
from fastapi import HTTPException, status
from typing import Optional


# Demo API keys for testing
DEMO_API_KEYS = {
    "demo-key-123": "Demo User",
    "test-key-456": "Test User",
    "dev-key-789": "Developer"
}


def verify_api_key(api_key: Optional[str]) -> bool:
    """Verify API key (simplified for testing)"""
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required"
        )
    
    if api_key not in DEMO_API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return True


def get_user_from_api_key(api_key: str) -> Optional[str]:
    """Get user name from API key"""
    return DEMO_API_KEYS.get(api_key)


def add_security_headers(response):
    """Add basic security headers"""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response
