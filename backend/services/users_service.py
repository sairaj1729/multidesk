import logging
from typing import List, Optional
from datetime import datetime
from db import get_database
from models.auth import UserInDB, UserResponse
from models.users import UserFilter

logger = logging.getLogger(__name__)

class UsersService:
    async def get_users(self, filter_params: UserFilter, page: int = 1, size: int = 50) -> dict:
        """Get users with filtering and pagination"""
        try:
            db = get_database()
            users_collection = db.users
            
            # Build query based on filters
            query = {}
            
            if filter_params.search:
                query["$or"] = [
                    {"first_name": {"$regex": filter_params.search, "$options": "i"}},
                    {"last_name": {"$regex": filter_params.search, "$options": "i"}},
                    {"email": {"$regex": filter_params.search, "$options": "i"}}
                ]
            
            if filter_params.role:
                query["role"] = filter_params.role
            
            if filter_params.status:
                # Assuming status refers to verification status
                is_verified = filter_params.status.lower() == "active"
                query["is_verified"] = is_verified
            
            # Calculate pagination
            skip = (page - 1) * size
            
            # Get total count
            total = await users_collection.count_documents(query)
            
            # Get users with pagination
            cursor = users_collection.find(query).skip(skip).limit(size).sort("created_at", -1)
            users = []
            async for doc in cursor:
                user = UserResponse(
                    id=str(doc["_id"]),
                    email=doc["email"],
                    first_name=doc["first_name"],
                    last_name=doc["last_name"],
                    role=doc["role"],
                    is_verified=doc.get("is_verified", False),
                    created_at=doc["created_at"],
                    updated_at=doc["updated_at"]
                )
                users.append(user)
            
            return {
                "users": users,
                "total": total,
                "page": page,
                "size": size
            }
            
        except Exception as e:
            logger.error(f"Failed to get users: {e}")
            return {
                "users": [],
                "total": 0,
                "page": page,
                "size": size
            }

    async def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        """Get a specific user by ID"""
        try:
            db = get_database()
            users_collection = db.users
            
            doc = await users_collection.find_one({"_id": user_id})
            if doc:
                return UserResponse(
                    id=str(doc["_id"]),
                    email=doc["email"],
                    first_name=doc["first_name"],
                    last_name=doc["last_name"],
                    role=doc["role"],
                    is_verified=doc.get("is_verified", False),
                    created_at=doc["created_at"],
                    updated_at=doc["updated_at"]
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user {user_id}: {e}")
            return None

# Create global users service instance
users_service = UsersService()