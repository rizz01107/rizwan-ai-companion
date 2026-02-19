from typing import List, Dict, Optional

class Memory:
    """
    Enhanced in-memory storage that supports session-based history.
    Ensures that different users don't see each other's conversation history.
    """

    def __init__(self, max_history: int = 10):
        # Dictionary to store history per user or session
        self.sessions: Dict[str, List[Dict[str, str]]] = {}
        self.max_history = max_history

    def add(self, session_id: str, user_message: str, bot_response: str) -> None:
        """
        Stores a conversation pair for a specific session.
        """
        if not session_id:
            return

        if session_id not in self.sessions:
            self.sessions[session_id] = []

        self.sessions[session_id].append({
            "user": user_message,
            "bot": bot_response
        })

        # Limit memory to max_history to save tokens/RAM
        if len(self.sessions[session_id]) > self.max_history:
            self.sessions[session_id].pop(0)

    def get_context(self, session_id: str) -> str:
        """
        Returns a formatted string of the conversation history for AI context.
        """
        if session_id not in self.sessions or not self.sessions[session_id]:
            return ""

        # Formatting context for better AI understanding
        context_parts = []
        for chat in self.sessions[session_id]:
            context_parts.append(f"User: {chat['user']}")
            context_parts.append(f"Assistant: {chat['bot']}")
            
        return "\n".join(context_parts)

    def clear(self, session_id: Optional[str] = None) -> None:
        """
        Clears history.
        """
        if session_id:
            self.sessions.pop(session_id, None)
        else:
            self.sessions.clear()

# Global instance
memory_manager = Memory()