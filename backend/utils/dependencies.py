from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.auth_service import auth_service
from models.auth import UserInDB
from typing import Optional
import logging

logger = logging.getLogger(__name__)
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserInDB:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        logger.info(f"🔐 Attempting to verify token: {token[:20]}...")
        
        token_data = await auth_service.verify_token(token)
        if token_data is None or token_data.email is None:
            logger.warning("❌ Token verification failed: invalid token data")
            raise credentials_exception
            
        logger.info(f"✓ Token verified for email: {token_data.email}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Token verification error: {e}")
        raise credentials_exception
    
    user = await auth_service.get_user_by_email(token_data.email)
    if user is None:
        logger.warning(f"❌ User not found for email: {token_data.email}")
        raise credentials_exception
    
    logger.info(f"✅ User authenticated: {user.email} (verified: {user.is_verified})")
    return user

async def get_current_verified_user(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
    """Get current verified user"""
    logger.info(f"📝 Checking verification status for: {current_user.email}")
    if not current_user.is_verified:
        logger.warning(f"⚠️ User {current_user.email} is NOT VERIFIED - returning 403")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please verify your email to access this resource."
        )
    logger.info(f"✅ User {current_user.email} is verified")
    return current_user

async def get_current_admin_user(current_user: UserInDB = Depends(get_current_verified_user)) -> UserInDB:
    """Get current admin user"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user