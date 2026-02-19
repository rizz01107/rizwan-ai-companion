import asyncio
import sys
import os
from pathlib import Path

# --- 🛠️ Robust Path Handling ---
# Project root (Rizwan_AI_Project/) ko Python path mein add karna
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

try:
    from backend.database.db import engine, Base
    # Models ko register karne ke liye import lazmi hai
    from backend.database import models 
except ImportError as e:
    print(f"❌ Import Error: Make sure you are running from the project root. {e}")
    sys.exit(1)

# ✅ Ye function app.py dhoond raha hai
async def init_db():
    """
    Standard function name for backend startup event.
    """
    await create_tables(reset=False)

async def create_tables(reset=False):
    """
    Creates all database tables defined in models.py.
    """
    try:
        async with engine.begin() as conn:
            if reset:
                print("⚠️ WARNING: Dropping all existing tables (Resetting Database)...")
                await conn.run_sync(Base.metadata.drop_all)
            
            print("🚀 Syncing Database Models...")
            await conn.run_sync(Base.metadata.create_all)
        
        print("✅ Database tables (Users & ChatHistory) are ready!")
        print(f"📍 Database File: {BASE_DIR}/rizwan_ai.db")
    except Exception as e:
        print(f"❌ Error during table creation: {e}")
        raise e

if __name__ == "__main__":
    # --- 💡 Rizwan's Setup Tip ---
    # Agar tables mein koi column change kiya ho, to isay True kar ke ek baar run karein.
    RESET_DB = False 
    
    # OS Check for Windows Pro-tip: 
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    try:
        asyncio.run(create_tables(reset=RESET_DB))
    except Exception as e:
        print(f"❌ Error during manual database setup: {e}")