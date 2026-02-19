from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging

# Logging setup
logger = logging.getLogger(__name__)

# Proper Imports with Safety Fallbacks
try:
    from backend.models.mood_analyzer import predict_mood
    from backend.models.emotion_detector import detect_emotion
    from backend.models.personality_analyzer import analyze_personality
except ImportError as e:
    logger.error(f"❌ Import Error in Analysis Routes: {e}")
    # Temporary fallbacks for development if files are missing
    predict_mood = lambda x: ("unknown", 0.0)
    detect_emotion = lambda x: "neutral"
    analyze_personality = lambda x: "undetermined"

router = APIRouter(prefix="/analyze", tags=["Model Testing"])

class TextRequest(BaseModel):
    text: str
    
    class Config:
        json_schema_extra = {
            "example": {"text": "I am feeling very productive today!"}
        }

@router.post("/all")
async def analyze_full(request: TextRequest):
    """
    Combined analysis: Mood, Emotion, and Personality.
    Useful for frontend dashboards or debugging.
    """
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Input text cannot be empty.")

    try:
        # 1. Mood Analysis (Safe unpacking)
        mood_result = predict_mood(request.text)
        if isinstance(mood_result, (tuple, list)) and len(mood_result) >= 2:
            mood_label, mood_score = mood_result[0], mood_result[1]
        else:
            mood_label, mood_score = mood_result, "N/A"

        # 2. Emotion Detection
        emotion = detect_emotion(request.text)

        # 3. Personality Profiling
        personality = analyze_personality(request.text)

        return {
            "status": "success",
            "results": {
                "mood": {
                    "label": mood_label,
                    "confidence": mood_score
                },
                "emotion": emotion,
                "personality": personality
            }
        }

    except Exception as e:
        logger.error(f"❌ Analysis Route Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing analysis: {str(e)}")