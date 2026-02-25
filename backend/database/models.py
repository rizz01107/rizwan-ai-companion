from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import sys
import os

# --- 🛠️ Import Base ---
try:
    from backend.database.db import Base
except ImportError:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(os.path.dirname(current_dir))
    if parent_dir not in sys.path:
        sys.path.append(parent_dir)
    from database.db import Base

# --- 👤 User Model ---
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    chats = relationship("ChatHistory", back_populates="user", cascade="all, delete-orphan")

# --- 💬 Chat History Model (Fixed for WhatsApp) ---
class ChatHistory(Base):
    """
    Stores interactions. Fixed to support both Web (user_id) and WhatsApp (phone_number).
    """
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    
    # WhatsApp support ke liye phone_number add kiya
    # Web users ke liye user_id ko nullable kiya
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    phone_number = Column(String(20), nullable=True, index=True) 
    
    user_input = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    
    mood_tag = Column(String(50), nullable=True, index=True) 
    emotion_tag = Column(String(50), nullable=True)
    personality_tag = Column(String(50), nullable=True) 

    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    user = relationship("User", back_populates="chats")

def init_models(engine):
    Base.metadata.create_all(bind=engine)
    print("🚀 [Database] Tables initialized successfully.")