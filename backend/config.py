import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Project Root Path
BASE_DIR = Path(__file__).resolve().parent

# =========================
# 🗄️ Database Configuration
# =========================
# sqlite+aiosqlite use karna async processing ke liye best hai
SQLITE_DB_PATH = os.path.join(BASE_DIR, "rizwan_ai.db")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{SQLITE_DB_PATH}")

# =========================
# 🔐 Security Configuration
# =========================
# Tip: Production mein ye key .env se hi aani chahiye
SECRET_KEY = os.getenv("SECRET_KEY", "rizwan_super_secret_key_2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours validity

# =========================
# 🤖 AI API Configuration (Gemini)
# =========================
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY", "AIzaSyDyAfeVJCv8UncHVWoNCW0F__yraQBI_S0")

# Validation check
if not GEMINI_API_KEY or "your_" in GEMINI_API_KEY:
    import logging
    logging.warning("⚠️ WARNING: Gemini API Key is missing or invalid in .env!")