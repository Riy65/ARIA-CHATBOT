from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from database import get_db
from ai_client import extract_profile_facts
from models.chat import ChatMessage, ChatSession
from models.profile import DocumentLinkCreate, ProfileUpdate, UploadedFile, UserProfile
from models.user import User
from utils.auth import get_current_user

router = APIRouter()


def current_db_user(db: Session, claims: dict) -> User:
    return db.scalar(select(User).where(User.email == claims["email"]))


def serialize_profile(profile: UserProfile | None, email: str) -> dict:
    if not profile:
        return {"email": email, "full_name": None, "headline": None, "location": None, "target_role": None, "bio": None, "linkedin_url": None, "website_url": None, "manual_details": {}}
    return {"email": email, "full_name": profile.full_name, "headline": profile.headline, "location": profile.location, "target_role": profile.target_role, "bio": profile.bio, "linkedin_url": profile.linkedin_url, "website_url": profile.website_url, "manual_details": profile.manual_details or {}}


def filter_profile_draft(draft: dict) -> dict:
    allowed_fields = {"full_name", "headline", "location", "target_role", "bio", "linkedin_url", "website_url", "manual_details"}
    return {field: value for field, value in draft.items() if field in allowed_fields and value is not None}


@router.get("")
def get_profile(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    user = current_db_user(db, current_user)
    profile = db.scalar(select(UserProfile).where(UserProfile.user_id == user.id))
    return serialize_profile(profile, user.email)


@router.put("")
def update_profile(payload: ProfileUpdate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    user = current_db_user(db, current_user)
    profile = db.scalar(select(UserProfile).where(UserProfile.user_id == user.id))
    if not profile:
        profile = UserProfile(user_id=user.id)
        db.add(profile)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, field, str(value) if field.endswith("_url") and value is not None else value)
    db.commit()
    db.refresh(profile)
    return serialize_profile(profile, user.email)


@router.post("/sources", status_code=201)
def save_professional_link(payload: DocumentLinkCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    user = current_db_user(db, current_user)
    source = UploadedFile(user_id=user.id, source_type=payload.source_type, title=payload.title, source_url=str(payload.source_url), extraction_status="pending")
    db.add(source)
    db.commit()
    db.refresh(source)
    return {"source_id": str(source.id), "source_type": source.source_type, "title": source.title, "source_url": source.source_url, "extraction_status": source.extraction_status}


@router.get("/sources")
def get_professional_sources(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    user = current_db_user(db, current_user)
    sources = db.scalars(select(UploadedFile).where(UploadedFile.user_id == user.id).order_by(desc(UploadedFile.created_at))).all()
    return [{"source_id": str(item.id), "source_type": item.source_type, "title": item.title, "source_url": item.source_url, "original_filename": item.original_filename, "content_type": item.content_type, "size_bytes": item.size_bytes, "extraction_status": item.extraction_status, "created_at": item.created_at} for item in sources]


@router.post("/drafts/from-chat/{conversation_id}")
def create_profile_draft_from_chat(conversation_id: UUID, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a review-only profile draft from one of the user's conversations."""
    user = current_db_user(db, current_user)
    session = db.scalar(select(ChatSession).where(ChatSession.id == conversation_id, ChatSession.user_id == user.id))
    if not session:
        raise HTTPException(status_code=404, detail="Conversation not found")
    messages = db.scalars(select(ChatMessage).where(ChatMessage.session_id == session.id, ChatMessage.role == "user").order_by(desc(ChatMessage.created_at)).limit(50)).all()
    if not messages:
        raise HTTPException(status_code=422, detail="This conversation has no user-provided details to extract")
    messages.reverse()
    try:
        draft = filter_profile_draft(extract_profile_facts([message.content for message in messages]))
    except Exception:
        raise HTTPException(status_code=503, detail="Profile extraction is temporarily unavailable. Please try again shortly.")
    return {"source_conversation_id": str(session.id), "draft": draft, "confirmation_required": True, "confirmation_endpoint": "PUT /profile"}
