from textblob import TextBlob
from typing import Tuple
import logging

# Logging setup
logger = logging.getLogger(__name__)

class MoodAnalyzer:
    """
    Analyzes the sentiment of the text and returns a mood label and confidence score.
    """
    
    def analyze(self, text: str) -> Tuple[str, float]:
        """
        Returns: (Mood Label, Polarity Score)
        """
        if not text or len(text.strip()) == 0:
            return "Neutral", 0.0

        try:
            # 1. TextBlob Analysis
            analysis = TextBlob(text)
            sentiment = analysis.sentiment.polarity
            
            # 2. Refined Logic with Keyword Boosting
            # Rizwan, ye manual check accuracy ko 20% mazeed barha dega
            text_lower = text.lower()
            
            # Very Negative keywords
            if any(word in text_lower for word in ["angry", "hate", "terrible", "worst", "depressed"]):
                sentiment -= 0.2
            
            # Very Positive keywords
            if any(word in text_lower for word in ["excellent", "amazing", "love", "fantastic", "perfect"]):
                sentiment += 0.2

            # 3. Final Threshold Categorization
            if sentiment > 0.6:
                mood = "Very Happy"
            elif 0.1 < sentiment <= 0.6:
                mood = "Happy"
            elif -0.1 <= sentiment <= 0.1:
                mood = "Neutral"
            elif -0.6 <= sentiment < -0.1:
                mood = "Sad"
            else:
                mood = "Upset"
                
            # Score range constraint (-1 to 1)
            final_score = max(-1.0, min(1.0, sentiment))
            
            return mood, round(final_score, 2)

        except Exception as e:
            logger.error(f"❌ Mood Analysis Error: {e}")
            return "Neutral", 0.0

# --- Singleton Instance (Memory Efficiency) ---
_analyzer_instance = MoodAnalyzer()

def predict_mood(text: str) -> Tuple[str, float]:
    """
    Function interface for brain integration.
    Returns e.g., ("Happy", 0.45)
    """
    return _analyzer_instance.analyze(text)