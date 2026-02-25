from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from pydantic import BaseModel
from typing import Optional, List, Dict
import logging
from datetime import datetime, timedelta, timezone

# 🛠️ INTERNAL IMPORTS
try:
    from backend.api_routes.auth_utils import decode_access_token
    from backend.database.db import get_db
    from backend.database.models import ChatHistory
    from backend.ai_engine.brain import generate_ai, brain
    from backend.ai_engine.memory import memory_manager
    from backend.ai_engine.image_gen import generate_image_url 
except ImportError:
    from .auth_utils import decode_access_token
    from ..database.db import get_db
    from ..database.models import ChatHistory
    from ..ai_engine.brain import generate_ai, brain
    from ..ai_engine.memory import memory_manager
    from ..ai_engine.image_gen import generate_image_url

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Chat Engine"])

# --- Pydantic Schemas ---
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    status: str
    response: str
    user_id: Optional[str] = None
    mood: Optional[str] = None
    image_url: Optional[str] = None  

# --- Helper: DB se Memory Recover karna ---
async def recover_memory_from_db(user_id: int, db: AsyncSession):
    try:
        stmt = (
            select(ChatHistory)
            .where(ChatHistory.user_id == user_id)
            .order_by(ChatHistory.timestamp.desc())
            .limit(5)
        )
        result = await db.execute(stmt)
        history = result.scalars().all()
        
        for chat in reversed(history):
            memory_manager.add(str(user_id), chat.user_input, chat.ai_response)
    except Exception as e:
        logger.error(f"Memory Recovery Error: {e}")

# --- 🚀 Main Chat Endpoint ---
@router.post("/send", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest, 
    db: AsyncSession = Depends(get_db),
    authorization: Optional[str] = Header(None) 
):
    # 1. Auth Check
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Please login first.")

    token = authorization.split(" ")[1]
    payload = decode_access_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Session expired")
    
    user_id_str = str(payload.get("sub"))
    user_id_int = int(user_id_str)
    
    user_message = request.message.strip()
    if not user_message:
        raise HTTPException(status_code=400, detail="Empty message")

    try:
        # 2. Context Management
        history_context = memory_manager.get_context(user_id_str)
        if not history_context:
            await recover_memory_from_db(user_id_int, db)
            history_context = memory_manager.get_context(user_id_str)

        # 3. Image Request Detection
        image_keywords = ["image", "photo", "picture", "draw", "generate", "banao", "dikhao", "art", "tasveer"]
        is_image_req = any(word in user_message.lower() for word in image_keywords)
        
        generated_img_url = None
        if is_image_req:
            # FIXED: Image generation can be slow, ensure it's handled or awaited if async
            generated_img_url = generate_image_url(user_message)
            ai_reply = "I've created this image for you! ✨"
        else:
            # FIXED: Awaiting the async AI call
            ai_reply_data = await generate_ai(user_message, context=history_context)
            if isinstance(ai_reply_data, dict):
                ai_reply = ai_reply_data.get("ai_response", "I'm not sure how to respond.")
            else:
                ai_reply = ai_reply_data

        # 4. Mood Analysis (Directly from Brain or Fallback)
        detected_mood = getattr(brain, 'last_mood', 'Neutral')
        detected_emotion = getattr(brain, 'last_emotion', 'Calm')
        
        # 5. Save to Memory & Database
        try:
            memory_manager.add(user_id_str, user_message, ai_reply)
            
            new_chat = ChatHistory(
                user_id=user_id_int,
                user_input=user_message,
                ai_response=ai_reply,
                mood_tag=detected_mood,
                emotion_tag=detected_emotion,
                timestamp=datetime.now(timezone.utc)
            )
            db.add(new_chat)
            await db.commit()
        except Exception as db_err:
            await db.rollback()
            logger.error(f"⚠️ DB Save Error: {db_err}")

        return ChatResponse(
            status="success",
            response=ai_reply,
            user_id=user_id_str,
            mood=detected_mood,
            image_url=generated_img_url 
        )

    except Exception as e:
        logger.error(f"❌ Chat Endpoint Error: {str(e)}")
        raise HTTPException(status_code=500, detail="AI Companion is busy, try again.")

# --- 📈 Get Mood History (For Chart.js) ---
@router.get("/history-stats")
async def get_mood_history(
    authorization: Optional[str] = Header(None), 
    db: AsyncSession = Depends(get_db)
):
    if not authorization:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        token = authorization.split(" ")[1]
        payload = decode_access_token(token)
        user_id = int(payload.get("sub"))
        
        # Pichlay 7 din ka data filter karein
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
        
        # SQL: Count moods grouped by their tag
        stmt = (
            select(ChatHistory.mood_tag, func.count(ChatHistory.mood_tag))
            .where(and_(ChatHistory.user_id == user_id, ChatHistory.timestamp >= seven_days_ago))
            .group_by(ChatHistory.mood_tag)
        )
        
        result = await db.execute(stmt)
        rows = result.all()

        # Data format for Chart.js
        labels = [str(row[0]) for row in rows if row[0]]
        values = [int(row[1]) for row in rows if row[0]]

        # Agar koi data na ho to empty arrays na bhejein (Optional improvement)
        if not labels:
            labels, values = ["No Data Yet"], [0]

        return {
            "status": "success",
            "labels": labels,
            "values": values
        }
    except Exception as e:
        logger.error(f"❌ Stats Error: {str(e)}")
        return {"status": "error", "labels": [], "values": []}