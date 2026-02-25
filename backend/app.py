import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys
import os
import inspect

# --- 🛠️ 1. Setup Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
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

# --- 📦 3. CORS Configuration ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 📦 4. Router Inclusion ---
init_db_func = None

try:
    import backend.init_db as database_initializer
    # Routes import karein
    from backend.api_routes import chat_routes, auth_routes, whatsapp_routes
    
    # Check if database initializer exists
    if hasattr(database_initializer, "init_db"):
        init_db_func = database_initializer.init_db
        logger.info("✅ Found 'init_db' function.")

    # --- ROUTER REGISTRATION ---
    
    # 1. Auth: http://127.0.0.1:8000/auth/login
    app.include_router(auth_routes.router, prefix="/auth", tags=["Authentication"]) 
    
    # 2. Chat & Stats: http://127.0.0.1:8000/api/chat/send AND /api/chat/history-stats
    app.include_router(chat_routes.router, prefix="/api/chat", tags=["Chat Engine"])
    
    # 3. WhatsApp: http://127.0.0.1:8000/whatsapp/message
    app.include_router(whatsapp_routes.router, prefix="/whatsapp", tags=["WhatsApp"])
    
    logger.info("✅ All routes loaded successfully.")

except ImportError as e:
    logger.error(f"❌ Critical Import Error: {str(e)}")

# --- 🛠 5. Database Initialization ---
@app.on_event("startup")
async def on_startup():
    logger.info("🚀 Starting up Rizwan AI Companion...")
    if init_db_func:
        try:
            if inspect.iscoroutinefunction(init_db_func):
                await init_db_func()
            else:
                init_db_func()
            logger.info("✅ Database tables are verified/ready.")
        except Exception as e:
            logger.error(f"❌ Failed to initialize database: {e}")

# --- 🏥 6. System Health Check ---
@app.get("/", tags=["System"])
async def root():
    return {
        "message": "Welcome to Rizwan AI Companion API",
        "developer": "Muhammad Rizwan",
        "status": "online",
        "university": "Islamia University of Bahawalpur"
    }

# --- 🏃 7. Run Server ---
if __name__ == "__main__":
    uvicorn.run("backend.app:app", host="127.0.0.1", port=8000, reload=True)