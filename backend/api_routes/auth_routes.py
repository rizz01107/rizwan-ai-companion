from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import logging

# =========================
# 🛠️ PROFESSIONAL IMPORTS
# =========================
try:
    from backend.api_routes.auth_utils import hash_password, verify_password, create_access_token
    from backend.database.db import get_db
    from backend.database.models import User
except ImportError:
    from .auth_utils import hash_password, verify_password, create_access_token
    from ..database.db import get_db
    from ..database.models import User

# Router setup - Tags for Swagger UI documentation
router = APIRouter(tags=["Authentication"])
logger = logging.getLogger(__name__)

# =========================
# 📌 Schemas (Validation)
# =========================
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, example="rizwan_ai")
    email: EmailStr = Field(..., example="rizwan@example.com")
    password: str = Field(..., min_length=8, example="strongpass123")

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    username: Optional[str] = None

class RegisterResponse(BaseModel):
    message: str
    user_id: int

# =========================
# 🚀 Register Endpoint
# =========================
@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Creates a new user account with hashed password storage.
    """
    try:
        # 1. Check if user already exists
        # We check both email and username to ensure uniqueness
        query = select(User).where((User.email == user.email) | (User.username == user.username))
        result = await db.execute(query)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            detail_msg = "Email already registered" if existing_user.email == user.email else "Username taken"
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=detail_msg
            )

        # 2. Create new user instance
        new_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hash_password(user.password) # Single hash as discussed
        )

        db.add(new_user)
        
        # 3. Commit and Refresh
        await db.commit()
        await db.refresh(new_user)
        
        logger.info(f"✅ User {user.username} (ID: {new_user.id}) registered.")
        return RegisterResponse(
            message="Account created successfully",
            user_id=new_user.id
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"❌ Registration Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Registration failed due to server error."
        )

# =========================
# 🔐 Login Endpoint
# =========================
@router.post("/login", response_model=TokenResponse)
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Authenticates user and returns a JWT Access Token.
    """
    try:
        # 1. Fetch user
        query = select(User).where(User.email == user.email)
        result = await db.execute(query)
        db_user = result.scalar_one_or_none()

        # 2. Verify existence and password
        # Professional tip: Use a generic error message for security
        if not db_user or not verify_password(user.password, db_user.hashed_password):
            logger.warning(f"🔑 Failed login attempt: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        # 3. Create Token
        # 'sub' should always be a string for JWT standards
        token_data = {
            "sub": str(db_user.id),
            "email": db_user.email,
            "username": db_user.username
        }
        
        access_token = create_access_token(data=token_data)

        logger.info(f"🔓 User {db_user.username} session started.")
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            username=db_user.username
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Login Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Login failed. Please try again later."
        )