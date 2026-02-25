from fastapi import APIRouter, Form, Response, Depends
from twilio.twiml.messaging_response import MessagingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
import logging

# Database imports
from backend.database.db import get_db
from backend.database.models import ChatHistory

# Setup Logger
logger = logging.getLogger(__name__)

# AI Engine imports with safe fallback
try:
    from backend.ai_engine.brain import generate_ai 
except ImportError as e:
    logger.error(f"❌ Module Import Error: {e}")
    async def generate_ai(text, context=""): 
        return {"ai_response": "I'm currently updating my brain.", "mood": "Neutral"}

router = APIRouter()

@router.post("/message")
async def handle_whatsapp(
    Body: str = Form(None), 
    From: str = Form(None), 
    db: AsyncSession = Depends(get_db)
):
    """
    Twilio Webhook for WhatsApp - Optimized by Rizwan's Assistant
    """
    # 1. Validation: Agar Twilio se empty request aaye
    if not Body or not From:
        logger.warning("⚠️ Received empty request from Twilio.")
        resp = MessagingResponse()
        return Response(content=str(resp), media_type="application/xml")

    user_message = Body.strip()
    # Normalize phone number (Remove 'whatsapp:' prefix)
    raw_phone = From.replace("whatsapp:", "") if "whatsapp:" in From else From

    try:
        # 2. Context Retrieval: Purani baaton ko yaad rakhne ke liye
        stmt = (
            select(ChatHistory)
            .where(ChatHistory.phone_number == raw_phone)
            .order_by(ChatHistory.timestamp.desc())
            .limit(5)
        )
        result = await db.execute(stmt)
        history_records = result.scalars().all()

        context = ""
        # Reverse taake purani chat pehle aaye aur naye wali baad mein
        for rec in reversed(history_records):
            context += f"User: {rec.user_input}\nAI: {rec.ai_response}\n"

        # 3. AI Engine Interaction: Response generate karna
        try:
            brain_output = await generate_ai(user_message, context=context)
            ai_reply = brain_output.get("ai_response", "I'm thinking...")
            mood_label = brain_output.get("mood", "Neutral")
            emotion_tag = brain_output.get("emotion", "calm")
            personality_tag = brain_output.get("personality", "friendly")
        except Exception as ai_err:
            logger.error(f"❌ AI Logic Error: {ai_err}")
            ai_reply = "I'm having a bit of trouble thinking right now. Talk to you soon!"
            mood_label, emotion_tag, personality_tag = "Neutral", "error", "neutral"

        # 4. Save to Database: Rizwan, history save karna zaroori hai
        new_chat = ChatHistory(
            phone_number=raw_phone,
            user_input=user_message,
            ai_response=ai_reply,
            mood_tag=mood_label,
            emotion_tag=emotion_tag,
            personality_tag=personality_tag,
            timestamp=datetime.now(timezone.utc)
        )
        db.add(new_chat)
        await db.commit() # Database mein pakka save karein

        # 5. Build TwiML Response
        resp = MessagingResponse()
        mood_icons = {
            "Very Happy": "🌟", 
            "Happy": "😊", 
            "Sad": "🫂", 
            "Upset": "💢", 
            "Neutral": "✨"
        }
        icon = mood_icons.get(mood_label, "🤖")
        
        # Branding and Formatting
        formatted_response = f"{ai_reply}\n\n{icon} *Rizwan AI Companion*"
        resp.message(formatted_response)

        # 6. Return Clean XML to Twilio
        return Response(
            content=str(resp), 
            media_type="application/xml"
        )

    except Exception as e:
        if db:
            await db.rollback()
        logger.error(f"❌ Critical WhatsApp Error: {e}")
        
        # Emergency Response
        error_resp = MessagingResponse()
        error_resp.message("🛠️ System Note: I'm rebooting a part of my brain. Talk to you in a second!")
        return Response(content=str(error_resp), media_type="application/xml")