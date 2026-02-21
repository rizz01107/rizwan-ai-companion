from textblob import TextBlob
import logging

# Logging setup
logger = logging.getLogger(__name__)

class PersonalityAnalyzer:
    """
    Rizwan's Personality Engine: 
    Analyzes traits using Sentiment, Roman Urdu Context, and Academic background.
    """

    def analyze(self, text: str) -> str:
        if not text or len(text.strip()) == 0:
            return "Quiet & Observant"

        try:
            text_lower = text.lower().strip()
            words = text_lower.split()
            word_count = len(words)
            
            # --- 1. Roman Urdu Context Mapping ---
            # Expanded dictionaries for better detection
            urdu_positive = ["acha", "theek", "khush", "behtreen", "fit", "mazay", "shukriya", "zabardast", "vibe"]
            urdu_negative = ["sad", "pareshan", "masla", "thaka", "bor", "gusa", "kharab", "tension", "fazool"]
            
            has_urdu_pos = any(w in text_lower for w in urdu_positive)
            has_urdu_neg = any(w in text_lower for w in urdu_negative)

            # --- 2. Sentiment & Subjectivity ---
            analysis = TextBlob(text)
            polarity = analysis.sentiment.polarity
            subjectivity = analysis.sentiment.subjectivity
            
            # --- 3. Advanced Intent Detection ---
            # Identifying Roman Urdu and English questions
            urdu_ques = ["kia", "kyun", "kab", "kahan", "kaise", "kesa", "kesi", "hai na"]
            is_question = "?" in text or text_lower.startswith(("what", "how", "why", "who", "when", "is", "are", "can")) or \
                          any(text_lower.startswith(q) for q in urdu_ques)

            # --- 🚀 Personality Mapping Logic ---

            # A. Academic & Career Focus (Specific to Muhammad Rizwan, BSAI Student)
            tech_keywords = ["ai", "python", "coding", "data", "university", "iub", "semester", "bsai", "machine learning", "project"]
            if any(k in text_lower for k in tech_keywords):
                return "Visionary & Tech-Minded"

            # B. Long-Form Analysis (Expressive users)
            if word_count > 15:
                if polarity > 0.2 or has_urdu_pos:
                    return "Optimistic & Expressive"
                elif polarity < -0.2 or has_urdu_neg:
                    return "Analytical & Critical"
                elif subjectivity > 0.6:
                    return "Deeply Reflective"
                else:
                    return "Detailed & Objective"
            
            # C. Short to Mid-Range Interaction
            else:
                if is_question:
                    return "Inquisitive & Engaging" if word_count > 5 else "Direct & Curious"
                
                # Sentiment-Driven Categorization
                if polarity > 0.3 or has_urdu_pos:
                    return "Friendly & Enthusiastic"
                elif polarity < -0.3 or has_urdu_neg:
                    return "Reserved & Frustrated"
                
                # Abstract & Brief
                if subjectivity > 0.6:
                    return "Intuitive & Creative"
                elif word_count < 4:
                    return "Stoic & Concise"
                else:
                    return "Balanced & Practical"

        except Exception as e:
            logger.error(f"❌ Personality Analysis Error for Rizwan's input: {e}")
            return "Friendly & Neutral"

# --- Singleton Instance for Efficiency ---
_personality_instance = PersonalityAnalyzer()

def analyze_personality(text: str) -> str:
    """
    Main entry point for the Brain to get personality tags.
    """
    return _personality_instance.analyze(text)