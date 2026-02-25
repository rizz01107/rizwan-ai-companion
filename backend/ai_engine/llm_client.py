import logging
import os
import asyncio
from typing import Optional
from dotenv import load_dotenv
from groq import AsyncGroq

# --------------------------------------------------
# 1. Configuration & Logging
# --------------------------------------------------
load_dotenv()
logger = logging.getLogger(__name__)

if not logger.hasHandlers():
    logging.basicConfig(level=logging.INFO)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# --------------------------------------------------
# 2. Initialize Async Groq Client
# --------------------------------------------------
client = None

def init_client():
    """Helper to initialize client without proxy conflicts"""
    global client
    try:
        if not GROQ_API_KEY:
            logger.error("❌ CRITICAL: GROQ_API_KEY is missing in your .env file!")
            return None
        # Standard initialization for 2026 stable environments
        return AsyncGroq(api_key=GROQ_API_KEY)
    except Exception as e:
        logger.error(f"❌ Failed to initialize Groq Client: {e}")
        return None

client = init_client()

# --------------------------------------------------
# 3. Model Priority
# --------------------------------------------------
MODEL_PRIORITY = [
    "llama-3.3-70b-versatile", 
    "llama-3.1-8b-instant",    
    "mixtral-8x7b-32768"       
]

# --------------------------------------------------
# 4. Core Generator Function (Async)
# --------------------------------------------------
async def generate_llm(structured_prompt: str) -> str:
    """
    Asynchronously generates a response from Groq with automatic model fallback.
    """
    global client
    
    # Lazy initialization if first attempt failed
    if client is None:
        client = init_client()
        if client is None:
            return "❌ Error: AI Engine not initialized. Check API Key."

    if not structured_prompt or not structured_prompt.strip():
        return "⚠️ Error: The AI received an empty prompt."

    last_error = "Unknown Connection Error"

    for model_id in MODEL_PRIORITY:
        try:
            logger.info(f"🔄 Processing request with model: {model_id}")

            response = await client.chat.completions.create(
                model=model_id,
                messages=[
                    {
                        "role": "user", 
                        "content": structured_prompt
                    }
                ],
                temperature=0.65,
                max_tokens=1024,
                top_p=0.9
            )

            if response.choices and response.choices[0].message.content:
                ai_text = response.choices[0].message.content.strip()
                logger.info(f"✅ Successfully generated response using {model_id}")
                return ai_text

        except Exception as e:
            error_str = str(e).lower()
            last_error = error_str
            
            # Rate Limit Handling
            if "429" in error_str or "rate_limit" in error_str:
                logger.warning(f"⚠️ Rate limit hit for {model_id}. Switching...")
                await asyncio.sleep(0.5) 
                continue
            
            # Auth Error
            if "401" in error_str:
                logger.error("❌ Authentication Failed: Invalid Groq API Key.")
                return "❌ AI Authentication Error: Please check backend configuration."

            logger.error(f"❌ Error with {model_id}: {error_str}")
            continue

    return f"⚠️ I'm temporarily unavailable. (Reason: {last_error[:60]}...)"