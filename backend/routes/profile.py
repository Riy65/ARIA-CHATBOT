from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from database import get_db
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
