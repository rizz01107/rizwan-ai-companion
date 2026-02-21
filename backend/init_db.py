import asyncio
import sys
import os
from pathlib import Path

# --- 🛠️ 1. Robust Path Handling ---
# Project root (Rizwan AI Companion/) ko Python path mein add karna
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

try:
    # Database engine aur Base ko backend.database.db se import karna
    from backend.database.db import engine, Base
    # Models ko import karna taake SQLAlchemy ko pata ho kaunse tables banane hain
    from backend.database import models 
except ImportError as e:
    print(f"❌ Import Error: Path issue or missing files. {e}")
    # Local debugging ke liye path print karein
    print(f"Current Sys Path: {sys.path[0]}")
    sys.exit(1)

# --- 🛠️ 2. Core Functions ---

async def init_db():
    """
    Standard function called by app.py during startup.
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
            # Ye line models.py ke saare tables create karegi
            await conn.run_sync(Base.metadata.create_all)
        
        print("✅ Database tables are ready!")
        # Database path clear dikhane ke liye
        db_path = os.path.join(BASE_DIR, "rizwan_ai.db")
        print(f"📍 Database Location: {db_path}")
        
    except Exception as e:
        print(f"❌ Error during table creation: {e}")
        # Isay raise karein taake app.py ko pata chale startup fail hua hai
        raise e

# --- 🛠️ 3. Execution Logic ---

if __name__ == "__main__":
    # Agar aapne models.py mein koi naya column add kiya hai, to isay True karke run karein
    RESET_DB = False 
    
    # Windows par Loop Policy ka masla hal karne ke liye
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    print("🛠️ Manual Database Setup Tool")
    try:
        asyncio.run(create_tables(reset=RESET_DB))
    except KeyboardInterrupt:
        print("\n🛑 Setup interrupted by user.")
    except Exception as e:
        print(f"❌ Failed to setup database manually: {e}")