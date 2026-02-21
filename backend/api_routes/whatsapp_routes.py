from fastapi import APIRouter, Form, Response, Depends
from twilio.twiml.messaging_response import MessagingResponse
from sqlalchemy.orm import Session
from backend.ai_engine.brain import generate_ai 
from backend.models.personality_analyzer import analyze_personality
from backend.database.database import get_db, ChatHistory

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])

@router.post("/message")
async def handle_whatsapp(
    Body: str = Form(None), 
    From: str = Form(None), 
    db: Session = Depends(get_db)
):
    # 1. Agar Body khali hai toh empty response
    if not Body:
        return Response(content="", media_type="application/xml")

    user_message = Body.strip()
    user_phone = From if From else "Unknown"

    # 2. Get Context from Database (Memory)
    history_records = db.query(ChatHistory).filter(ChatHistory.phone_number == user_phone).order_by(ChatHistory.timestamp.desc()).limit(5).all()
    context = ""
    for rec in reversed(history_records):
        context += f"User: {rec.user_message}\nAI: {rec.ai_response}\n"

    # 3. Analyze Mood
    try:
        mood_tag = analyze_personality(user_message)
    except:
        mood_tag = "Neutral"
    
    # 4. Get AI Reply
    # System Instruction: Humne prompt mein likh diya ke user Rizwan hai
    prompt_with_identity = f"Tumhara user Rizwan hai. Context: {context}\nUser: {user_message}"
    try:
        ai_reply = generate_ai(prompt_with_identity, context=context)
    except Exception as e:
        ai_reply = "Rizwan, server thora slow hai, dobara try karein."

    # 5. Database mein save karein
    try:
        new_chat = ChatHistory(phone_number=user_phone, user_message=user_message, ai_response=ai_reply)
        db.add(new_chat)
        db.commit()
    except:
        pass

    # 6. STRICT TWIML RESPONSE (Yehi main cheez hai)
    resp = MessagingResponse()
    resp.message(f"{ai_reply}\n\n🎭 Mood: {mood_tag}")
    
    # Twilio ko batana ke ye XML hai aur Ngrok warning bypass karna
    return Response(
        content=str(resp),
        media_type="application/xml",
        headers={
            "Content-Type": "application/xml",
            "ngrok-skip-browser-warning": "true"
        }
    )