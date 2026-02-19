from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging

# Logging setup
logger = logging.getLogger(__name__)

# Correct Import for your structure
try:
    from backend.models.mood_analyzer import predict_mood
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    try:
        from models.mood_analyzer import predict_mood
    except ImportError:
        logger.error("❌ Mood analyzer model file missing!")
        predict_mood = lambda x: ("Neutral", 0.0)

router = APIRouter(prefix="/ai", tags=["Testing"])

# Pydantic model for JSON validation
class MoodRequest(BaseModel):
    text: str

@router.post("/predict-mood")
async def mood_predict(request: MoodRequest):
    """
    Testing endpoint to check Mood Analysis logic.
    """
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    try:
        # Calling the ML logic
        result = predict_mood(request.text)
        
        # Safe Unpacking (Handling both tuple and single value returns)
        if isinstance(result, (tuple, list)) and len(result) >= 2:
            label, score = result[0], result[1]
        else:
            label, score = result, "N/A"
        
        return {
            "status": "success",
            "data": {
                "text": request.text,
                "mood_label": label,
                "confidence_score": score
            }
        }
    except Exception as e:
        logger.error(f"❌ Testing Route Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Model error: {str(e)}")