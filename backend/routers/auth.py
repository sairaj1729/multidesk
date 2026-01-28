from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from models.auth import (
    UserCreate, 
    UserLogin, 
    UserResponse, 
    OTPVerification, 
    OTPRequest, 
    PasswordReset, 
    Token
)
from services.auth_service import auth_service
from services.email_service import email_service
from utils.dependencies import get_current_user
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=dict)
async def register_user(user_create: UserCreate):
    """Register a new user"""
    try:
        # Create user
        user = await auth_service.create_user(user_create)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
        
        # Send verification OTP
        otp = await email_service.send_verification_otp(user.email)
        if not otp:
            # User created but email failed - still success
            logger.warning(f"User created but failed to send verification email to {user.email}")
            return {
                "message": "User registered successfully. Please check your email for verification.",
                "email_sent": False
            }
        
        return {
            "message": "User registered successfully. Please check your email for verification OTP.",
            "email_sent": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration failed for {user_create.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=Token)
async def login_user(user_login: UserLogin):
    """Login user"""
    try:
        # Authenticate user
        user = await auth_service.authenticate_user(user_login.email, user_login.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=auth_service.access_token_expire_minutes)
        access_token = auth_service.create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        # Convert user to response format
        user_response = auth_service.user_to_response(user)
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed for {user_login.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.post("/verify-email", response_model=dict)
async def verify_email(otp_verification: OTPVerification):
    """Verify user email with OTP"""
    try:
        # Verify OTP
        is_valid = await email_service.verify_otp(
            otp_verification.email, 
            otp_verification.otp, 
            "verification"
        )
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired OTP"
            )
        
        # Mark user as verified
        success = await auth_service.verify_user_email(otp_verification.email)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to verify user"
            )
        
        return {"message": "Email verified successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Email verification failed for {otp_verification.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email verification failed"
        )

@router.post("/resend-verification", response_model=dict)
async def resend_verification_otp(otp_request: OTPRequest):
    """Resend verification OTP"""
    try:
        # Check if user exists
        user = await auth_service.get_user_by_email(otp_request.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already verified"
            )
        
        # Send verification OTP
        otp = await email_service.send_verification_otp(otp_request.email)
        if not otp:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send verification email"
            )
        
        return {"message": "Verification OTP sent successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Resend verification failed for {otp_request.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resend verification OTP"
        )

@router.post("/forgot-password", response_model=dict)
async def forgot_password(otp_request: OTPRequest):
    """Send password reset OTP"""
    try:
        # Check if user exists
        user = await auth_service.get_user_by_email(otp_request.email)
        if not user:
            # Don't reveal if email exists or not for security
            return {"message": "If your email is registered, you will receive a password reset OTP"}
        
        # Send password reset OTP
        otp = await email_service.send_password_reset_otp(otp_request.email)
        if not otp:
            logger.error(f"Failed to send password reset OTP to {otp_request.email}")
        
        return {"message": "If your email is registered, you will receive a password reset OTP"}
        
    except Exception as e:
        logger.error(f"Forgot password failed for {otp_request.email}: {e}")
        return {"message": "If your email is registered, you will receive a password reset OTP"}

@router.post("/reset-password", response_model=dict)
async def reset_password(password_reset: PasswordReset):
    """Reset password with OTP"""
    try:
        # Verify OTP
        is_valid = await email_service.verify_otp(
            password_reset.email, 
            password_reset.otp, 
            "password_reset"
        )
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired OTP"
            )
        
        # Update password
        success = await auth_service.update_user_password(
            password_reset.email, 
            password_reset.new_password
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update password"
            )
        
        return {"message": "Password reset successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password reset failed for {password_reset.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user = Depends(get_current_user)):
    """Get current user information"""
    return auth_service.user_to_response(current_user)

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "authentication"}