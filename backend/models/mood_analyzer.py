from textblob import TextBlob
from typing import Tuple
import logging

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MoodAnalyzer:
    """
    Analyzes the sentiment of text and returns a mood label and polarity score.
    Enhanced with manual keyword boosting and Roman Urdu support for 
    Muhammad Rizwan's AI Companion.
    """
    
    def analyze(self, text: str) -> Tuple[str, float]:
        """
        Calculates mood by combining TextBlob sentiment with manual keyword intensity.
        Returns: (Mood Label, Polarity Score)
        """
        if not text or len(text.strip()) == 0:
            return "Neutral", 0.0

        try:
            # 1. TextBlob Base Analysis
            analysis = TextBlob(text)
            sentiment = analysis.sentiment.polarity
            
            # 2. Refined Logic with Keyword Boosting
            text_lower = text.lower().strip()
            
            # Very Negative keywords (English + Roman Urdu)
            neg_keywords = [
                "angry", "hate", "terrible", "worst", "depressed", "sad", 
                "disappointed", "kill", "die", "bakwas", "gussa", "buri"
            ]
            if any(word in text_lower for word in neg_keywords):
                sentiment -= 0.20 # Increased weight for high-impact words
            
            # Very Positive keywords (English + Roman Urdu)
            pos_keywords = [
                "excellent", "amazing", "love", "fantastic", "perfect", 
                "great", "best", "brilliant", "achha", "shukriya", "behtreen"
            ]
            if any(word in text_lower for word in pos_keywords):
                sentiment += 0.20

            # 3. Punctuation Intensity Check
            # Multiple exclamation marks often signal intense emotion
            if "!" in text:
                if sentiment > 0:
                    sentiment += 0.05
                elif sentiment < 0:
                    sentiment -= 0.05

            # 4. Final Threshold Categorization
            # Logic refined to ensure "Very Happy" and "Upset" are harder to trigger than "Happy/Sad"
            if sentiment > 0.7:
                mood = "Very Happy"
            elif 0.15 < sentiment <= 0.7:
                mood = "Happy"
            elif -0.15 <= sentiment <= 0.15:
                mood = "Neutral"
            elif -0.7 <= sentiment < -0.15:
                mood = "Sad"
            else:
                mood = "Upset"
                
            # 5. Constraints & Return
            # Ensure the final score stays within the standard [-1.0, 1.0] range
            final_score = max(-1.0, min(1.0, sentiment))
            
            logger.info(f"📊 Analysis: '{text[:20]}...' -> {mood} ({final_score})")
            return mood, round(float(final_score), 2)

        except Exception as e:
            logger.error(f"❌ Mood Analysis Error: {e}")
            return "Neutral", 0.0

# --- Singleton Instance ---
# Initializing once to save memory on your FastAPI server
_analyzer_instance = MoodAnalyzer()

def predict_mood(text: str) -> Tuple[str, float]:
    """
    Standard interface to be used by brain.py, chat_routes.py, and whatsapp_routes.py.
    Example: mood, score = predict_mood("This is fantastic!")
    """
    return _analyzer_instance.analyze(text)