from datetime import datetime

def chat_message(conversation_id, user_id: str, role: str, content: str):
    return {
        "conversation_id": conversation_id,
        "user_id": user_id,
        "role": role,          # "user" or "bot"
        "content": content,
        "timestamp": datetime.utcnow()
    }
