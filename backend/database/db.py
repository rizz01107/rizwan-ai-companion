import logging
import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.exc import SQLAlchemyError

# --- 1. Robust Path Handling ---
# Ensuring backend can be found even if script is run directly
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# Import DATABASE_URL from config
try:
    from backend.config import DATABASE_URL
except ImportError:
    # Fallback for local testing
    DATABASE_URL = "sqlite+aiosqlite:///./rizwan_ai.db"

# Setup Logging
logger = logging.getLogger(__name__)

# --- 2. Async Engine Setup ---
# pool_pre_ping ensures the connection is alive before use
# connect_args={"check_same_thread": False} is mandatory for SQLite + FastAPI
engine = create_async_engine(
    DATABASE_URL, 
    echo=False, 
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# --- 3. Session Maker ---
# 2026 Best Practice: Using async_sessionmaker
AsyncSessionLocal = async_sessionmaker(
    bind=engine, 
    expire_on_commit=False, 
    class_=AsyncSession
)

# --- 4. Base Class ---
Base = declarative_base()

# --- 5. Database Dependency for FastAPI ---
async def get_db():
    """
    Asynchronous generator to provide database sessions to FastAPI routes.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            # We don't commit here; the route handler handles commit/rollback
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"❌ Database session error: {str(e)}")
            raise e
        finally:
            # Session is closed automatically by the 'async with' block
            await session.close()

# --- 6. Initialization Function ---
async def init_db():
    """
    Creates all tables defined in the models.
    Called during app startup in app.py.
    """
    try:
        # ✅ FIX: Import models locally inside function to avoid Circular Imports
        from backend.database import models 
        
        async with engine.begin() as conn:
            # This line syncs SQLAlchemy models with the actual SQLite file
            await conn.run_sync(Base.metadata.create_all)
            
        logger.info("✅ Database tables (User, ChatHistory) verified and ready.")
    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")
        # We raise this so app.py knows the startup failed
        raise e