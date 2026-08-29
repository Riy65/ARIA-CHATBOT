from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from ai_client import generate_chat_title, get_ai_reply
from database import get_db
from models.chat import ChatMessage, ChatRequest, ChatSession
from models.user import User
from utils.auth import get_current_user

router = APIRouter()


def current_db_user(db: Session, claims: dict) -> User:
    user = db.scalar(select(User).where(User.email == claims["email"]))
    if not user:
        raise HTTPException(status_code=401, detail="User account no longer exists")
    return user


def serialize_message(message: ChatMessage) -> dict:
    return {"role": message.role, "content": message.content, "timestamp": message.created_at}


@router.post("/new")
def create_conversation(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    user = current_db_user(db, current_user)
    session = ChatSession(user_id=user.id)
    db.add(session)
    db.commit()
    db.refresh(session)
    return {"conversation_id": str(session.id), "title": session.title}


@router.post("/send")
def send_message(request: ChatRequest, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    user = current_db_user(db, current_user)
    session = db.scalar(select(ChatSession).where(ChatSession.id == request.conversation_id, ChatSession.user_id == user.id))
    if not session:
        raise HTTPException(status_code=404, detail="Conversation not found")

    db.add(ChatMessage(session_id=session.id, role="user", content=request.message.strip()))
    db.commit()
    history = list(db.scalars(select(ChatMessage).where(ChatMessage.session_id == session.id).order_by(desc(ChatMessage.created_at)).limit(20)))
    history.reverse()
    messages = [{"role": "system", "content": "You are Aria, a helpful, concise portfolio-building assistant. Ask focused follow-up questions and give practical recommendations."}]
    if session.context_summary:
        messages.append({"role": "system", "content": f"Earlier session context: {session.context_summary}"})
    messages.extend({"role": item.role, "content": item.content} for item in history)
    try:
        ai_reply = get_ai_reply(messages)
    except Exception:
        ai_reply = "Aria is temporarily unavailable. Your message has been saved; please try again shortly."

    db.add(ChatMessage(session_id=session.id, role="assistant", content=ai_reply))
    if session.title == "New Portfolio Chat":
        try:
            session.title = generate_chat_title(request.message, ai_reply)[:160] or session.title
        except Exception:
            session.title = request.message.strip()[:57] or session.title
    session.updated_at = datetime.now(timezone.utc)
    db.commit()
    return {"reply": ai_reply, "title": session.title}


@router.get("/conversations")
def get_conversations(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    user = current_db_user(db, current_user)
    sessions = db.scalars(select(ChatSession).where(ChatSession.user_id == user.id).order_by(desc(ChatSession.updated_at))).all()
    return [{"conversation_id": str(item.id), "title": item.title, "updated_at": item.updated_at} for item in sessions]


@router.get("/messages/{conversation_id}")
def get_messages(conversation_id: UUID, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    user = current_db_user(db, current_user)
    session = db.scalar(select(ChatSession).where(ChatSession.id == conversation_id, ChatSession.user_id == user.id))
    if not session:
        raise HTTPException(status_code=404, detail="Conversation not found")
    messages = db.scalars(select(ChatMessage).where(ChatMessage.session_id == session.id).order_by(ChatMessage.created_at)).all()
    return [serialize_message(item) for item in messages]


@router.delete("/conversation/{conversation_id}")
def delete_conversation(conversation_id: UUID, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    user = current_db_user(db, current_user)
    session = db.scalar(select(ChatSession).where(ChatSession.id == conversation_id, ChatSession.user_id == user.id))
    if not session:
        raise HTTPException(status_code=404, detail="Conversation not found")
    db.delete(session)
    db.commit()
    return {"message": "Conversation deleted"}
