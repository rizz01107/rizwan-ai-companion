from textblob import TextBlob
import logging

# Logging setup
logger = logging.getLogger(__name__)

class EmotionDetector:
    """
    Detects basic emotions based on sentiment intensity, subjectivity, 
    and specific keyword mapping for higher accuracy.
    """
    
    def __init__(self):
        # Expanded keyword mapping for 2026 AI standards
        self.keywords = {
            "excited": ["wow", "amazing", "can't wait", "finally", "great", "hurray", "super", "awesome", "yay"],
            "angry": ["hate", "angry", "stop", "stupid", "worst", "nonsense", "annoying", "shut up", "kill"],
            "anxious": ["worried", "nervous", "scared", "fear", "help", "stress", "panic", "anxiety", "unsure"],
            "sad": ["lonely", "crying", "sad", "hopeless", "unhappy", "broke", "miss", "pain"],
            "surprised": ["unbelievable", "really?", "shocked", "omg", "whoa", "surprising"],
            "confused": ["what?", "how?", "don't understand", "confused", "meaningless", "why"]
        }

    def detect(self, text: str) -> str:
        if not text or len(text.strip()) == 0:
            return "Neutral"

        try:
            clean_text = text.lower()
            
            # 1. Keyword Check (Highest Priority)
            # Rizwan, ye specific emotions ko polarity se pehle pakar leta hai
            for emotion, words in self.keywords.items():
                if any(word in clean_text for word in words):
                    return emotion.capitalize()

            # 2. Sentiment & Subjectivity Analysis (TextBlob Fallback)
            analysis = TextBlob(text)
            polarity = analysis.sentiment.polarity
            subjectivity = analysis.sentiment.subjectivity 

            # logic mapping based on sentiment scores
            if polarity > 0.6:
                return "Joyful"
            elif 0.1 < polarity <= 0.6:
                return "Positive"
            elif -0.1 >= polarity > -0.6:
                return "Frustrated"
            elif polarity <= -0.6:
                return "Distressed"
            
            # 3. Subjectivity check: Agar text facts se zyada feelings par ho
            if subjectivity > 0.7:
                return "Emotional"
            elif 0.4 < subjectivity <= 0.7:
                return "Reflective"
                
            return "Calm"

        except Exception as e:
            logger.error(f"❌ Emotion Detection Error: {e}")
            return "Calm"

# --- Singleton Instance (Memory Efficiency for your BSAI Project) ---
_detector_instance = EmotionDetector()

def detect_emotion(text: str) -> str:
    """
    Wrapper function for brain integration.
    Usage: emotion = detect_emotion("I am so stressed about exams")
    """
    return _detector_instance.detect(text)