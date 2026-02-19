from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging

# Logging setup
logger = logging.getLogger(__name__)

# Proper relative import structure with safety fallback
try:
    from backend.models.mood_analyzer import predict_mood
except ImportError:
    try:
        from ..models.mood_analyzer import predict_mood
    except ImportError as e:
        logger.error(f"❌ Mood Analyzer Model not found: {e}")
        # Fallback function if model is missing
        predict_mood = lambda x: ("Neutral", 0.0)

router = APIRouter(prefix="/analyze", tags=["Analysis"])

# Request Schema
class TextRequest(BaseModel):
    text: str

@router.post("/mood")
async def mood_predict(request: TextRequest):
    """
    Directly predicts mood from the given text for testing purposes.
    """
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    try:
        # predict_mood returns (label, score)
        result = predict_mood(request.text)
        
        # Safe unpacking logic
        if isinstance(result, (tuple, list)) and len(result) >= 2:
            label, score = result[0], result[1]
        else:
            label, score = result, 0.0
        
        return {
            "status": "success",
            "input": request.text,
            "prediction": {
                "label": label,
                "confidence_score": f"{score:.2f}" if isinstance(score, float) else score
            }
        }
    except Exception as e:
        logger.error(f"❌ Mood Route Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")