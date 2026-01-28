from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from models.auth import UserCreate, UserInDB, UserResponse, TokenData
from db import get_database
from config import settings
import logging
from bson import ObjectId

logger = logging.getLogger(__name__)

# Password hashing - fallback to sha256_crypt if bcrypt has issues
pwd_context = CryptContext(
    schemes=["sha256_crypt", "bcrypt"],
    deprecated="auto",
    sha256_crypt__rounds=5000,
    bcrypt__rounds=12
)


class AuthService:
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES

    def get_password_hash(self, password: str) -> str:
        """Generate password hash"""
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    async def verify_token(self, token: str) -> Optional[TokenData]:
        """Verify and decode access token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            email: str = payload.get("sub")
            if email is None:
                logger.warning("Token payload missing 'sub' field")
                return None
            token_data = TokenData(email=email)
            logger.debug(f"Token verified successfully for: {email}")
            return token_data
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except JWTError as e:
            logger.warning(f"JWT verification failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during token verification: {e}")
            return None

    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """Get user by email from database"""
        try:
            db = get_database()
            users_collection = db.users
            
            user_doc = await users_collection.find_one({"email": email})
            if user_doc:
                return UserInDB(
                    id=str(user_doc["_id"]),
                    email=user_doc["email"],
                    first_name=user_doc["first_name"],
                    last_name=user_doc["last_name"],
                    role=user_doc["role"],
                    hashed_password=user_doc["hashed_password"],
                    is_verified=user_doc.get("is_verified", False),
                    created_at=user_doc["created_at"],
                    updated_at=user_doc["updated_at"]
                )
            return None
        except Exception as e:
            logger.error(f"Failed to get user by email {email}: {e}")
            return None

    async def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        """Get user by ID from database"""
        try:
            db = get_database()
            users_collection = db.users
            
            user_doc = await users_collection.find_one({"_id": ObjectId(user_id)})
            if user_doc:
                return UserInDB(
                    id=str(user_doc["_id"]),
                    email=user_doc["email"],
                    first_name=user_doc["first_name"],
                    last_name=user_doc["last_name"],
                    role=user_doc["role"],
                    hashed_password=user_doc["hashed_password"],
                    is_verified=user_doc.get("is_verified", False),
                    created_at=user_doc["created_at"],
                    updated_at=user_doc["updated_at"]
                )
            return None
        except Exception as e:
            logger.error(f"Failed to get user by ID {user_id}: {e}")
            return None

    async def create_user(self, user_create: UserCreate) -> Optional[UserInDB]:
        """Create new user in database"""
        try:
            # Check if user already exists
            existing_user = await self.get_user_by_email(user_create.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )

            db = get_database()
            users_collection = db.users
            
            # Hash password
            try:
                hashed_password = self.get_password_hash(user_create.password)
            except Exception as e:
                logger.error(f"Password hashing failed: {e}")
                raise
            
            # Create user document
            user_doc = {
                "email": user_create.email,
                "first_name": user_create.first_name,
                "last_name": user_create.last_name,
                "role": user_create.role,
                "hashed_password": hashed_password,
                "is_verified": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Insert user
            result = await users_collection.insert_one(user_doc)
            
            if result.inserted_id:
                user_doc["_id"] = result.inserted_id
                return UserInDB(
                    id=str(result.inserted_id),
                    email=user_doc["email"],
                    first_name=user_doc["first_name"],
                    last_name=user_doc["last_name"],
                    role=user_doc["role"],
                    hashed_password=user_doc["hashed_password"],
                    is_verified=user_doc["is_verified"],
                    created_at=user_doc["created_at"],
                    updated_at=user_doc["updated_at"]
                )
            
            return None
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to create user {user_create.email}: {e}")
            return None

    async def authenticate_user(self, email: str, password: str) -> Optional[UserInDB]:
        """Authenticate user with email and password"""
        user = await self.get_user_by_email(email)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user

    async def verify_user_email(self, email: str) -> bool:
        """Mark user email as verified"""
        try:
            db = get_database()
            users_collection = db.users
            
            result = await users_collection.update_one(
                {"email": email},
                {
                    "$set": {
                        "is_verified": True,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Failed to verify user email {email}: {e}")
            return False

    async def update_user_password(self, email: str, new_password: str) -> bool:
        """Update user password"""
        try:
            db = get_database()
            users_collection = db.users
            
            hashed_password = self.get_password_hash(new_password)
            
            result = await users_collection.update_one(
                {"email": email},
                {
                    "$set": {
                        "hashed_password": hashed_password,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Failed to update password for {email}: {e}")
            return False

    def user_to_response(self, user: UserInDB) -> UserResponse:
        """Convert UserInDB to UserResponse"""
        return UserResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role,
            is_verified=user.is_verified,
            created_at=user.created_at,
            updated_at=user.updated_at
        )

# Create global auth service instance
auth_service = AuthService()