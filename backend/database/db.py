import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError

# Configuration import
try:
    from backend.config import DATABASE_URL
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config import DATABASE_URL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 1. Async Engine setup
# SQLite ke liye pool_pre_ping=True best hai connection loss se bachne ke liye
engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True)

# 2. Session Maker
AsyncSessionLocal = sessionmaker(
    bind=engine, 
    expire_on_commit=False, 
    class_=AsyncSession
)

# 3. Base Class
Base = declarative_base()

# 4. Database Dependency for FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"❌ Database session error: {str(e)}")
            raise
        finally:
            await session.close()

# 5. Initialization function
async def init_db():
    try:
        # ✅ IMPORTANT: Saare models yahan import karne honge 
        # taake 'Base' ko pata chal sake ke kon kon se tables banane hain
        from backend.database.models import User, ChatHistory 
        
        async with engine.begin() as conn:
            # Tables create karne ka process
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database tables (User, ChatHistory) initialized successfully.")
    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")
        raise e