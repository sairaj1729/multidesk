from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional
from models.users import UserListResponse, UserFilter
from services.users_service import users_service
from utils.dependencies import get_current_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/users", tags=["Users"])

@router.get("/", response_model=UserListResponse)
async def get_users(
    search: Optional[str] = Query(None, description="Search in user name or email"),
    role: Optional[str] = Query(None, description="Filter by role"),
    status: Optional[str] = Query(None, description="Filter by status (active/inactive)"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size"),
    current_user = Depends(get_current_user)
):
    """Get users with filtering and pagination"""
    try:
        # Only allow admin users to access all users
        # For now, we'll allow all authenticated users to see the user list
        filter_params = UserFilter(
            search=search,
            role=role,
            status=status
        )
        
        result = await users_service.get_users(filter_params, page, size)
        return UserListResponse(**result)
        
    except Exception as e:
        logger.error(f"Failed to get users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get users"
        )

@router.get("/{user_id}", response_model=dict)
async def get_user(user_id: str, current_user = Depends(get_current_user)):
    """Get a specific user by ID"""
    try:
        # Users can only access their own profile or admins can access any profile
        # For now, we'll allow users to access any profile
        user = await users_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user"
        )

@router.get("/list", response_model=dict)
async def get_user_list(current_user = Depends(get_current_user)):
    """Get list of users for dropdown selection"""
    try:
        # Get all users for the current account
        filter_params = UserFilter()
        result = await users_service.get_users(filter_params, 1, 1000)  # Get all users
        
        # Format users for dropdown
        user_list = [
            {
                "id": user.id,
                "name": f"{user.first_name} {user.last_name}",
                "email": user.email
            }
            for user in result["users"]
        ]
        
        return {"users": user_list}
        
    except Exception as e:
        logger.error(f"Failed to get user list for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user list"
        )