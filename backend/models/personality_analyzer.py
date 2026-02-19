from textblob import TextBlob
import logging

# Logging setup
logger = logging.getLogger(__name__)

class PersonalityAnalyzer:
    """
    Analyzes user personality traits based on sentence structure, 
    sentiment, verbosity, and curiosity.
    """

    def analyze(self, text: str) -> str:
        if not text or len(text.strip()) == 0:
            return "Quiet"

        try:
            words = text.split()
            word_count = len(words)
            analysis = TextBlob(text)
            polarity = analysis.sentiment.polarity
            subjectivity = analysis.sentiment.subjectivity
            
            # Additional AI Logic: Checking for curiosity (questions)
            is_question = "?" in text or text.lower().startswith(("what", "how", "why", "who", "when"))

            # --- 🚀 Advanced Categorization Logic ---
            
            # Case 1: Long/Detailed Input (Verbosity > 15 words)
            if word_count > 15:
                if polarity > 0.2:
                    return "Optimistic & Expressive"
                elif polarity < -0.2:
                    return "Analytical & Critical"
                elif subjectivity > 0.6:
                    return "Deeply Reflective"
                else:
                    return "Detailed & Objective"
            
            # Case 2: Mid-range or Short Input
            else:
                # Highly Curious Personality
                if is_question and word_count < 10:
                    return "Inquisitive & Direct"
                elif is_question:
                    return "Curious & Engaging"
                
                # Emotional Based
                if polarity > 0.3:
                    return "Friendly & Enthusiastic"
                elif polarity < -0.3:
                    return "Reserved & Frustrated"
                
                # Style Based
                elif subjectivity > 0.5:
                    return "Intuitive & Creative"
                elif word_count < 5:
                    return "Stoic & Concise"
                else:
                    return "Reserved & Balanced"

        except Exception as e:
            logger.error(f"❌ Personality Analysis Error: {e}")
            return "Standard/Friendly"

# --- Singleton Instance (Memory Efficiency) ---
_personality_instance = PersonalityAnalyzer()

def analyze_personality(text: str) -> str:
    """
    Wrapper for brain integration. 
    Usage in brain.py: personality = analyze_personality(user_text)
    """
    return _personality_instance.analyze(text)