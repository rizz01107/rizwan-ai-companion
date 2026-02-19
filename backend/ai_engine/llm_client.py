import logging
import os
from dotenv import load_dotenv
from groq import Groq
from time import sleep

# --------------------------------------------------
# Load Environment Variables
# --------------------------------------------------
load_dotenv()
logger = logging.getLogger(__name__)

# Basic logging setup check
if not logger.hasHandlers():
    logging.basicConfig(level=logging.INFO)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# --------------------------------------------------
# Initialize Groq Client
# --------------------------------------------------
try:
    if not GROQ_API_KEY:
        logger.error("❌ GROQ_API_KEY missing in .env file!")
        client = None
    else:
        client = Groq(api_key=GROQ_API_KEY)
        logger.info("✅ Groq API configured successfully with 2026 Stable Models.")
except Exception as e:
    logger.error(f"❌ Failed to initialize Groq Client: {e}")
    client = None


# --------------------------------------------------
# Model Priority List (Strictly 2026 Stable IDs)
# --------------------------------------------------
# Rizwan, purane Llama3 models decommission ho chuke hain, 
# isliye hum ye latest IDs use kar rahe hain.
MODEL_PRIORITY = [
    "llama-3.3-70b-versatile",   # 🧠 Sabse smart model
    "llama-3.1-8b-instant",      # ⚡ Sabse fast model
    "mixtral-8x7b-32768"         # 🔗 Backup model
]


# --------------------------------------------------
# LLM Generator Function
# --------------------------------------------------
def generate_llm(prompt: str) -> str:
    if not client:
        return "AI Client not initialized. Please check your Groq API key."

    if not prompt or not prompt.strip():
        return "Prompt cannot be empty."

    last_error = "Unknown Error"

    # Loop through models to find an available one
    for model_id in MODEL_PRIORITY:
        try:
            logger.info(f"🔄 Trying Groq model: {model_id}")

            response = client.chat.completions.create(
                model=model_id,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are Rizwan's AI Companion. Answer concisely and professionally."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=512
            )

            # Agar response mil jaye toh return karein
            if response and response.choices and response.choices[0].message.content:
                content = response.choices[0].message.content.strip()
                logger.info(f"✅ Success with model: {model_id}")
                return content

            logger.warning(f"⚠️ Model {model_id} returned an empty response.")
            continue

        except Exception as e:
            error_msg = str(e).lower()
            last_error = error_msg
            
            # 1. Rate Limit Handling (429)
            if "429" in error_msg or "rate_limit" in error_msg:
                logger.error(f"❌ Rate limit hit for {model_id}. Sleeping 1s...")
                sleep(1) # Chota sa break taake agla model chal sake
                continue
            
            # 2. Authentication / Invalid Key (401)
            if "401" in error_msg or "authentication" in error_msg:
                logger.error("❌ API Key is invalid!")
                return "❌ API Key Error: Please update your Groq Key."

            # 3. Model Retired / Decommissioned (400)
            if "decommissioned" in error_msg or "not found" in error_msg:
                logger.error(f"❌ Model {model_id} is no longer available.")
                continue

            # 4. Connection Issues
            logger.error(f"❌ Error with {model_id}: {error_msg}")
            continue

    # Agar koi bhi model kaam na kare
    return f"⚠️ All models failed. Last Error: {last_error[:50]}..."