from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
import logging
import sys
import os

# 🛠️ Fix Pathing (Ensuring backend root is in path)
# Is se VS Code aur Uvicorn dono ko 'backend' folder mil jayega
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

try:
    from backend.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
except ImportError:
    # Fallback for direct script execution or different root contexts
    SECRET_KEY = os.getenv("SECRET_KEY", "RIZWAN_SUPER_SECRET_KEY_2026")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 1440 # Default 24 hours

# Password hashing context - PBKDF2 is great for stability
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
logger = logging.getLogger(__name__)

# =========================
# 🔐 Password Hashing
# =========================

def hash_password(password: str) -> str:
    """Hashes a plain text password safely using PBKDF2."""
    if not password:
        return ""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against its stored hash."""
    if not plain_password or not hashed_password:
        return False
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"❌ Verification Error: {str(e)}")
        return False

# =========================
# 🎟 Create Access Token
# =========================

def create_access_token(data: dict) -> str:
    """Generates a secure JWT access token."""
    to_encode = data.copy()
    
    # Using timezone-aware UTC for 2026 standards
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "iat": now,
        "type": "access"
    })

    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logger.error(f"❌ Token Generation Error: {e}")
        return ""

# =========================
# 🔎 Decode Token
# =========================

def decode_access_token(token: str) -> dict:
    """Decodes and validates a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # 'sub' check ensures the token has a valid subject (user_id)
        if payload.get("sub") is None:
            return None
        return payload
    except JWTError as e:
        logger.warning(f"⚠️ JWT Decode Error: {str(e)}")
        return None