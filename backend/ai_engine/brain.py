import logging
import os
import asyncio
from typing import Optional, Dict, Any

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------------------------------------------------
# 🛠️ AI Analysis Models Imports
# --------------------------------------------------
try:
    from backend.models.mood_analyzer import predict_mood
    # Fallbacks for missing models to prevent crash
    try:
        from backend.models.emotion_detector import detect_emotion
    except ImportError:
        def detect_emotion(x): return "calm"
        
    try:
        from backend.models.personality_analyzer import analyze_personality
    except ImportError:
        def analyze_personality(x): return "friendly"
        
    from backend.ai_engine.llm_client import generate_llm
except ImportError as e:
    logger.warning(f"⚠️ Modules missing, using fallbacks. Error: {e}")
    predict_mood = lambda x: ("Neutral", 0.0)
    detect_emotion = lambda x: "calm"
    analyze_personality = lambda x: "friendly"
    async def generate_llm(p): return "AI model is currently unavailable."

class AIBrain:
    def __init__(self):
        self.name = "Rizwan AI Companion"

    async def process_user_input(self, text: str, context: str = "") -> Dict[str, Any]:
        """
        Asynchronously analyzes input and returns a Dictionary with response and tags.
        """
        if not text or len(text.strip()) == 0:
            return {
                "ai_response": "I'm listening, but I didn't get any text.",
                "mood": "Neutral", "emotion": "calm", "personality": "friendly"
            }

        try:
            # --- 1. AI Analysis Phase (Sync Models) ---
            try:
                mood_res = predict_mood(text)
                current_mood = mood_res[0] if isinstance(mood_res, (tuple, list)) else mood_res
            except: current_mood = "Neutral"

            try:
                current_emotion = detect_emotion(text)
            except: current_emotion = "thoughtful"

            try:
                current_personality = analyze_personality(text)
            except: current_personality = "empathetic"

            # --- 2. Advanced Prompt Engineering ---
            system_instruction = (
                f"Your name is {self.name}. You are the loyal AI Companion of Muhammad Rizwan. "
                f"Detected User State: Mood={current_mood}, Emotion={current_emotion}. "
                "Instructions: Be empathetic, concise, and friendly. "
                "Maintain memory of the previous context provided."
            )

            final_prompt = (
                f"SYSTEM: {system_instruction}\n"
                f"HISTORY:\n{context}\n"
                f"USER: {text}\n"
                f"AI RESPONSE:"
            )

            # --- 3. Generate Response (Async Call) ---
            logger.info(f"🧠 Brain analyzing: Mood={current_mood}, Emotion={current_emotion}")
            
            # This must be awaited because generate_llm is async
            ai_response = await generate_llm(final_prompt)

            if not ai_response:
                ai_response = "I'm processing a lot right now. Could you repeat that?"

            return {
                "ai_response": ai_response,
                "mood": current_mood,
                "emotion": current_emotion,
                "personality": current_personality
            }

        except Exception as e:
            logger.error(f"❌ Critical Brain Error: {str(e)}")
            return {
                "ai_response": "I'm having trouble thinking clearly. Let's try again.",
                "mood": "Neutral", "emotion": "error", "personality": "friendly"
            }

# --- Singleton Instance ---
brain = AIBrain()

async def generate_ai(text: str, context: str = "") -> Dict[str, Any]:
    """
    Asynchronous helper function for routes.
    """
    return await brain.process_user_input(text, context)