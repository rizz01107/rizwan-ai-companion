import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys
import os

# --- 🛠️ 1. Setup Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- 🛠️ 2. Path Fix ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

app = FastAPI(
    title="Rizwan AI Companion",
    description="An intelligent AI companion with Mood, Emotion, and Personality analysis.",
    version="1.1.0"
)

# --- 📦 3. Safe Imports & Router Inclusion ---
init_db_func = None
try:
    # Database and Routes Imports
    import backend.init_db as database_initializer
    from backend.api_routes import chat_routes, auth_routes, analysis_routes, whatsapp_routes
    
    # DB Init Function Check
    if hasattr(database_initializer, "init_db"):
        init_db_func = database_initializer.init_db
        logger.info("✅ Found 'init_db' function.")
    else:
        logger.warning("⚠️ Could not find 'init_db' function in init_db.py")

    # Include Routers
    app.include_router(auth_routes.router, tags=["Authentication"]) 
    app.include_router(chat_routes.router, tags=["Chat"])
    app.include_router(analysis_routes.router, tags=["Analysis"])
    app.include_router(whatsapp_routes.router, tags=["WhatsApp Integration"]) # WhatsApp Added
    
    logger.info("✅ All routes (Auth, Chat, Analysis, WhatsApp) loaded successfully.")

except ImportError as e:
    logger.error(f"❌ Import failed: {str(e)}")
    sys.exit(1)

# 🌍 4. CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🛠 5. Database Initialization on Startup
@app.on_event("startup")
async def on_startup():
    logger.info("🚀 Starting up Rizwan AI Companion...")
    if init_db_func:
        try:
            import inspect
            if inspect.iscoroutinefunction(init_db_func):
                await init_db_func()
            else:
                init_db_func()
            logger.info("✅ Database tables are ready.")
        except Exception as e:
            logger.error(f"❌ Failed to initialize database: {e}")
    else:
        logger.warning("⚠️ Skipping DB init: init_db function not found.")

# 🏥 6. Health Check
@app.get("/", tags=["System"])
async def root():
    return {
        "message": "Welcome to Rizwan AI Companion API",
        "status": "online",
        "developer": "Muhammad Rizwan (AI Enthusiast)"
    }

# 🏃 7. Run Server
if __name__ == "__main__":
    # Ensure the path matches your project structure
    uvicorn.run("backend.app:app", host="127.0.0.1", port=8000, reload=True)