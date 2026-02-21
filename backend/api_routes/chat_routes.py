from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from pydantic import BaseModel
from typing import Optional, List, Dict
import logging
from datetime import datetime, timedelta, timezone

# 🛠️ IMPORTS (With Error Handling)
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
router = APIRouter(prefix="/chat", tags=["Chat Engine"])

# --- Pydantic Schemas ---
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    status: str
    response: str
    user_id: Optional[str] = None
    mood: Optional[str] = None
    image_url: Optional[str] = None  

# --- Helper Function: Recover Memory from DB ---
async def recover_memory_from_db(user_id: int, db: AsyncSession):
    """Fetch last 5 chats from DB if RAM memory is empty"""
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

# --- 🚀 Chat Endpoint ---
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
    
    user_id_str = str(payload.get("sub"))
    user_id_int = int(user_id_str)
    
    user_message = request.message.strip()
    if not user_message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        # 2. Memory Context Management
        history_context = ""
        try:
            history_context = memory_manager.get_context(user_id_str)
            if not history_context:
                await recover_memory_from_db(user_id_int, db)
                history_context = memory_manager.get_context(user_id_str)
        except Exception as mem_err:
            logger.warning(f"Memory Error: {mem_err}")

        # 3. Detect Image Request (Improved Logic)
        image_keywords = ["image", "photo", "picture", "draw", "generate", "banao", "dikhao", "art"]
        is_image_req = any(word in user_message.lower() for word in image_keywords)
        
        generated_img_url = None
        if is_image_req:
            # Generate the URL using the engine we optimized earlier
            generated_img_url = generate_image_url(user_message)
            ai_reply = "I've processed your request! I am generating the image for you now... ✨"
        else:
            # Standard AI Text Reply
            ai_reply = generate_ai(user_message, context=history_context)

        # 4. Mood & Emotion Analysis
        # Ensure 'brain' has these attributes or provide defaults
        detected_mood = getattr(brain, 'last_mood', 'neutral')
        detected_emotion = getattr(brain, 'last_emotion', 'calm')
        
        # 5. Memory & DB Save
        try:
            # Add to local RAM memory
            memory_manager.add(user_id_str, user_message, ai_reply)
            
            # Save to Database
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
            await db.refresh(new_chat)
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
        logger.error(f"❌ Chat Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI processing failed: {str(e)}")

# --- 📈 Get Mood History ---
@router.get("/history-stats")
async def get_mood_history(
    authorization: Optional[str] = Header(None), 
    db: AsyncSession = Depends(get_db)
):
    if not authorization:
        raise HTTPException(status_code=401, detail="No token provided")
    
    try:
        token = authorization.split(" ")[1]
        payload = decode_access_token(token)
        if not payload:
             raise HTTPException(status_code=401, detail="Invalid token")
             
        user_id = int(payload.get("sub"))

        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
        
        stmt = (
            select(ChatHistory.mood_tag, func.count(ChatHistory.mood_tag))
            .where(and_(ChatHistory.user_id == user_id, ChatHistory.timestamp >= seven_days_ago))
            .group_by(ChatHistory.mood_tag)
        )
        
        result = await db.execute(stmt)
        rows = result.all()

        # Constructing clean labels and values for Chart.js
        labels = [str(row[0]) for row in rows if row[0] is not None]
        values = [int(row[1]) for row in rows if row[0] is not None]

        return {
            "status": "success",
            "labels": labels,
            "values": values,
            "summary": {str(k): v for k, v in rows}
        }
    except Exception as e:
        logger.error(f"❌ Stats Error: {str(e)}")
        return {"status": "error", "labels": [], "values": [], "detail": str(e)}