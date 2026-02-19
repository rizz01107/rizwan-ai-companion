import logging
import os
from typing import Optional

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------------------------------------------------
# 🛠️ AI Analysis Models Imports
# --------------------------------------------------
try:
    from backend.models.mood_analyzer import predict_mood
    from backend.models.emotion_detector import detect_emotion
    from backend.models.personality_analyzer import analyze_personality
    from backend.ai_engine.llm_client import generate_llm
except ImportError as e:
    logger.warning(f"⚠️ Models missing, using fallbacks. Error: {e}")
    
    # Placeholder functions taake code crash na ho
    predict_mood = lambda x: "neutral"
    detect_emotion = lambda x: "calm"
    analyze_personality = lambda x: "friendly"
    
    try:
        from backend.ai_engine.llm_client import generate_llm
    except ImportError:
        def generate_llm(p): return "Error: LLM Client (Groq/Gemini) not found."

class AIBrain:
    def __init__(self):
        self.name = "Rizwan AI Companion"
        # Rizwan, ye variables database mein stats save karne ke liye lazmi hain
        self.last_mood = "neutral"
        self.last_emotion = "calm"
        self.last_personality = "friendly"

    def process_user_input(self, text: str, context: str = "") -> str:
        """
        User ke input ko analyze karke personalized response banata hai.
        """
        if not text or len(text.strip()) == 0:
            return "I'm listening, but I didn't get any text. What's on your mind?"

        try:
            # --- 1. AI Analysis Phase ---
            # Hum user ka mood detect karke class variables mein save kar rahe hain
            try:
                mood_res = predict_mood(text)
                self.last_mood = mood_res[0] if isinstance(mood_res, (tuple, list)) else mood_res
            except: 
                self.last_mood = "neutral"

            try:
                self.last_emotion = detect_emotion(text)
            except: 
                self.last_emotion = "thoughtful"

            try:
                self.last_personality = analyze_personality(text)
            except: 
                self.last_personality = "empathetic"

            # --- 2. Advanced Prompt Engineering ---
            # AI ko context dena ke user kis haal mein hai
            system_meta = (
                f"Your name is {self.name}. You are a supportive AI. "
                f"Detected User State: Mood={self.last_mood}, Emotion={self.last_emotion}. "
                "Instructions: Be highly empathetic, concise, and professional. "
                "Maintain a natural flow like a human companion."
            )

            history_str = f"\n[Previous Conversations]:\n{context}\n" if context else ""
            
            final_prompt = (
                f"SYSTEM: {system_meta}\n"
                f"{history_str}"
                f"USER: {text}\n"
                f"AI:"
            )

            # --- 3. Generate Response ---
            logger.info(f"🧠 Brain analyzing: Mood={self.last_mood}, Emotion={self.last_emotion}")
            response = generate_llm(final_prompt)

            if not response:
                return "I'm processing a lot right now. Could you repeat that?"

            return response

        except Exception as e:
            logger.error(f"❌ Critical Brain Error: {str(e)}")
            return "I'm having a little trouble thinking clearly. Let's try again."

# --- Singleton Instance ---
brain = AIBrain()

def generate_ai(text: str, context: str = "") -> str:
    """
    Main helper function used by chat_routes.py
    """
    return brain.process_user_input(text, context)