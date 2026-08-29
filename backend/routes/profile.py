from io import BytesIO
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from docx import Document
from pypdf import PdfReader
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from database import get_db
from ai_client import extract_profile_facts, extract_from_document
from models.chat import ChatMessage, ChatSession
from models.profile import DocumentExtraction, DocumentLinkCreate, ProfileUpdate, UploadedFile, UserProfile
from models.user import User
from utils.auth import get_current_user

router = APIRouter()

MAX_UPLOAD_BYTES = 10 * 1024 * 1024
MAX_DOCUMENT_CHARACTERS = 24_000
ALLOWED_DOCUMENT_EXTENSIONS = {".pdf", ".docx", ".txt"}


def current_db_user(db: Session, claims: dict) -> User:
    return db.scalar(select(User).where(User.email == claims["email"]))


def serialize_profile(profile: UserProfile | None, email: str) -> dict:
    if not profile:
        return {"email": email, "full_name": None, "headline": None, "location": None, "target_role": None, "bio": None, "linkedin_url": None, "website_url": None, "manual_details": {}}
    return {"email": email, "full_name": profile.full_name, "headline": profile.headline, "location": profile.location, "target_role": profile.target_role, "bio": profile.bio, "linkedin_url": profile.linkedin_url, "website_url": profile.website_url, "manual_details": profile.manual_details or {}}


def filter_profile_draft(draft: dict) -> dict:
    allowed_fields = {"full_name", "headline", "location", "target_role", "bio", "linkedin_url", "website_url", "manual_details"}
    return {field: value for field, value in draft.items() if field in allowed_fields and value is not None}


def extract_document_text(file_content: bytes, filename: str) -> str:
    """Convert common resume formats to text before sending user-owned content to Gemini."""
    extension = Path(filename).suffix.lower()
    if extension == ".txt":
        text = file_content.decode("utf-8", errors="replace")
    elif extension == ".pdf":
        text = "\n".join(page.extract_text() or "" for page in PdfReader(BytesIO(file_content)).pages)
    elif extension == ".docx":
        document = Document(BytesIO(file_content))
        text = "\n".join(paragraph.text for paragraph in document.paragraphs)
    else:
        raise HTTPException(status_code=415, detail="Upload a PDF, DOCX, or TXT document")
    text = text.strip()
    if not text:
        raise HTTPException(status_code=422, detail="No readable text was found in this document")
    return text[:MAX_DOCUMENT_CHARACTERS]


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


@router.post("/uploads", status_code=201)
async def upload_document(file: UploadFile = File(...), current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    """Extract document facts with Gemini and retain safe context for later portfolio chats."""
    user = current_db_user(db, current_user)
    if not file.filename:
        raise HTTPException(status_code=400, detail="File must have a name")
    filename = Path(file.filename).name
    if Path(filename).suffix.lower() not in ALLOWED_DOCUMENT_EXTENSIONS:
        raise HTTPException(status_code=415, detail="Upload a PDF, DOCX, or TXT document")

    try:
        file_content = await file.read()
    finally:
        await file.close()
    if len(file_content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Files must be 10 MB or smaller")
    text_content = extract_document_text(file_content, filename)

    uploaded = UploadedFile(
        user_id=user.id,
        source_type="document",
        title=filename,
        original_filename=filename,
        content_type=file.content_type or "application/octet-stream",
        size_bytes=len(file_content),
        extraction_status="processing"
    )
    db.add(uploaded)
    db.commit()
    db.refresh(uploaded)
    
    try:
        extracted_facts = filter_profile_draft(extract_from_document(text_content, filename))
        if not extracted_facts:
            raise RuntimeError("Gemini did not return portfolio facts")
        db.add(DocumentExtraction(uploaded_file_id=uploaded.id, extracted_facts=extracted_facts, context_excerpt=text_content))
        uploaded.extraction_status = "completed"
    except Exception:
        uploaded.extraction_status = "failed"
    db.commit()

    return {
        "source_id": str(uploaded.id),
        "original_filename": uploaded.original_filename,
        "content_type": uploaded.content_type,
        "extraction_status": uploaded.extraction_status,
        "extracted_facts": extracted_facts if uploaded.extraction_status == "completed" else {},
    }


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
