from datetime import datetime
from typing import Any, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, HttpUrl
from sqlalchemy import DateTime, ForeignKey, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True)
    full_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    headline: Mapped[str | None] = mapped_column(String(220), nullable=True)
    location: Mapped[str | None] = mapped_column(String(160), nullable=True)
    target_role: Mapped[str | None] = mapped_column(String(160), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    linkedin_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    website_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    manual_details: Mapped[dict] = mapped_column(JSON, default=dict)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="profile")


class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    source_type: Mapped[str] = mapped_column(String(32))
    title: Mapped[str] = mapped_column(String(255))
    source_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    storage_key: Mapped[str | None] = mapped_column(String(512), nullable=True, unique=True)
    original_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    content_type: Mapped[str | None] = mapped_column(String(127), nullable=True)
    size_bytes: Mapped[int | None] = mapped_column(nullable=True)
    extraction_status: Mapped[str] = mapped_column(String(32), default="not_requested")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="uploaded_files")


class ProfileUpdate(BaseModel):
    full_name: str | None = Field(default=None, max_length=160)
    headline: str | None = Field(default=None, max_length=220)
    location: str | None = Field(default=None, max_length=160)
    target_role: str | None = Field(default=None, max_length=160)
    bio: str | None = Field(default=None, max_length=5000)
    linkedin_url: HttpUrl | None = None
    website_url: HttpUrl | None = None
    manual_details: dict[str, Any] | None = None


class DocumentLinkCreate(BaseModel):
    source_type: Literal["resume_link", "linkedin_profile", "other_link"]
    title: str = Field(min_length=1, max_length=255)
    source_url: HttpUrl
