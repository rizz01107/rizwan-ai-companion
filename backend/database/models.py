from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import sys
import os

# --- 🛠️ Import Base with Multi-Context Support ---
try:
    from backend.database.db import Base
except ImportError:
    # Handles cases where script is run from local folder or parent
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(os.path.dirname(current_dir))
    if parent_dir not in sys.path:
        sys.path.append(parent_dir)
    try:
        from database.db import Base
    except ImportError:
        # Final fallback
        from backend.database.db import Base

# --- 👤 User Model ---
class User(Base):
    """
    User model for storing authentication and profile details.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    # 2026 Best Practice: Using timezone-aware UTC
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships: One user can have many chats
    chats = relationship("ChatHistory", back_populates="user", cascade="all, delete-orphan")

# --- 💬 Chat History Model ---
class ChatHistory(Base):
    """
    Stores interactions between Muhammad Rizwan and the AI Companion.
    """
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    user_input = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    
    # --- 📊 Analytics Columns (Important for Graph) ---
    # In columns ka data hum "brain.py" se save karwayenge
    mood_tag = Column(String(50), nullable=True, index=True) 
    emotion_tag = Column(String(50), nullable=True)
    personality_tag = Column(String(50), nullable=True) # Extra analysis for better profile

    # Timestamp for mood tracking over time
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    # Relationship back to User
    user = relationship("User", back_populates="chats")

# --- 🧪 Helper for Database Initialization ---
# Is function ko app startup par call kiya ja sakta hai
def init_models(engine):
    Base.metadata.create_all(bind=engine)
    print("🚀 [Database] Tables initialized successfully.")