from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from pydantic import BaseModel
from typing import Optional, List, Dict
import logging
from datetime import datetime, timedelta, timezone

# ----------------------------------------------------------
# 🛠️ FIXED IMPORTS
# ----------------------------------------------------------
try:
    from backend.api_routes.auth_utils import decode_access_token
    from backend.database.db import get_db
    from backend.database.models import ChatHistory
    from backend.ai_engine.brain import generate_ai, brain
    from backend.ai_engine.memory import memory_manager
except ImportError:
    from .auth_utils import decode_access_token
    from ..database.db import get_db
    from ..database.models import ChatHistory
    from ..ai_engine.brain import generate_ai, brain
    from ..ai_engine.memory import memory_manager

# Logging setup
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat Engine"])

# -------------------------
# 📌 Pydantic Schemas
# -------------------------
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    status: str
    response: str
    user_id: Optional[str] = None
    mood: Optional[str] = None

# -------------------------
# 🚀 Chat Endpoint
# -------------------------
@router.post("/send", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest, 
    db: AsyncSession = Depends(get_db),
    authorization: Optional[str] = Header(None) 
):
    # 1. Bearer Token Verification
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized access")

    token = authorization.split(" ")[1]
    payload = decode_access_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Session expired")
    
    user_id = str(payload.get("sub"))
    
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        # 2. Get Memory Context
        history_context = ""
        try:
            history_context = memory_manager.get_context(user_id)
        except Exception: pass

        # 3. AI Reply
        ai_reply = generate_ai(request.message, context=history_context)

        # --- 📊 ASLI ANALYSIS EXTRACTION ---
        # Rizwan, yahan hum brain se puchte hain ke abhi kya analyze hua
        # (Assuming brain stores latest state after process_user_input)
        detected_mood = getattr(brain, 'last_mood', 'neutral')
        detected_emotion = getattr(brain, 'last_emotion', 'calm')
        
        # 4. Memory & DB Save
        try:
            memory_manager.add(user_id, request.message, ai_reply)
            
            new_chat = ChatHistory(
                user_id=int(user_id),
                user_input=request.message,
                ai_response=ai_reply,
                mood_tag=detected_mood,
                emotion_tag=detected_emotion
            )
            db.add(new_chat)
            await db.commit()
        except Exception as db_err:
            await db.rollback()
            logger.warning(f"⚠️ DB Save Error: {db_err}")

        return ChatResponse(
            status="success",
            response=ai_reply,
            user_id=user_id,
            mood=detected_mood
        )

    except Exception as e:
        logger.error(f"❌ Chat Error: {str(e)}")
        raise HTTPException(status_code=500, detail="AI processing failed.")

# -------------------------
# 📈 Get Mood History (Final Logic for Graph)
# -------------------------
@router.get("/history-stats")
async def get_mood_history(
    authorization: Optional[str] = Header(None), 
    db: AsyncSession = Depends(get_db)
):
    # 1. Verify User
    if not authorization:
        raise HTTPException(status_code=401, detail="No token")
    
    token = authorization.split(" ")[1]
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    user_id = int(payload.get("sub"))

    # 2. SQL Query: Count Moods for last 7 days
    try:
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
        
        # Query: SELECT mood_tag, COUNT(mood_tag) GROUP BY mood_tag
        stmt = (
            select(ChatHistory.mood_tag, func.count(ChatHistory.mood_tag))
            .where(and_(ChatHistory.user_id == user_id, ChatHistory.timestamp >= seven_days_ago))
            .group_by(ChatHistory.mood_tag)
        )
        
        result = await db.execute(stmt)
        rows = result.all()

        # Data format for Chart.js
        # Rizwan, ye labels aur values frontend ko graph banane mein madad denge
        labels = [row[0] for row in rows if row[0] is not None]
        values = [row[1] for row in rows if row[0] is not None]

        return {
            "status": "success",
            "labels": labels,
            "values": values,
            "summary": dict(rows)
        }

    except Exception as e:
        logger.error(f"❌ Stats Error: {str(e)}")
        return {"status": "error", "labels": [], "values": [], "detail": str(e)}