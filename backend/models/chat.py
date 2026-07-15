from pydantic import BaseModel


class ChatRequest(BaseModel):
    conversation_id: str
    message: str


class CreateConversationResponse(BaseModel):
    conversation_id: str
    title: str