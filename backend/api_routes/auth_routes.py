from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import logging

# =========================
# 🛠️ FIXED IMPORTS (Matching your actual folder structure)
# =========================
try:
    # Try importing using the full package path
    from backend.api_routes.auth_utils import hash_password, verify_password, create_access_token
    from backend.database.db import get_db
    from backend.database.models import User
except ImportError:
    # Relative fallback if the above fails (fixes VS Code resolution errors)
    try:
        from .auth_utils import hash_password, verify_password, create_access_token
        from ..database.db import get_db
        from ..database.models import User
    except ImportError as e:
        # Final safety if paths are still messy
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from api_routes.auth_utils import hash_password, verify_password, create_access_token
        from database.db import get_db
        from database.models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = logging.getLogger(__name__)

# =========================
# 📌 Pydantic Schemas
# =========================
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)

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
    try:
        # 1. Check if user already exists
        query = select(User).where((User.email == user.email) | (User.username == user.username))
        result = await db.execute(query)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            detail_msg = "Email already registered" if existing_user.email == user.email else "Username taken"
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=detail_msg
            )

        # 2. Create new user
        new_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hash_password(user.password)
        )

        db.add(new_user)
        
        # 3. Commit and handle DB error
        try:
            await db.commit()
            await db.refresh(new_user)
        except Exception as db_exc:
            await db.rollback()
            logger.error(f"❌ Database Commit Error: {db_exc}")
            raise HTTPException(status_code=500, detail="Could not save user to database.")

        return RegisterResponse(
            message="User registered successfully",
            user_id=new_user.id
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"❌ General Registration Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed due to server error.")

# =========================
# 🔐 Login Endpoint
# =========================
@router.post("/login", response_model=TokenResponse)
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    try:
        query = select(User).where(User.email == user.email)
        result = await db.execute(query)
        db_user = result.scalar_one_or_none()

        # Check user exists and password is correct
        if not db_user or not verify_password(user.password, db_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Create JWT Token
        access_token = create_access_token(
            data={
                "sub": str(db_user.id),
                "email": db_user.email,
                "username": db_user.username
            }
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            username=db_user.username
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"❌ Login Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error during login")