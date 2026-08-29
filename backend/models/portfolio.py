from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field
from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Portfolio(Base):
    __tablename__ = "portfolios"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(160))
    target_role: Mapped[str | None] = mapped_column(String(160), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="portfolios")
    versions = relationship("PortfolioVersion", back_populates="portfolio", cascade="all, delete-orphan", order_by="PortfolioVersion.version_number")


class PortfolioVersion(Base):
    __tablename__ = "portfolio_versions"
    __table_args__ = (UniqueConstraint("portfolio_id", "version_number", name="uq_portfolio_version_number"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    portfolio_id: Mapped[UUID] = mapped_column(ForeignKey("portfolios.id", ondelete="CASCADE"), index=True)
    version_number: Mapped[int] = mapped_column(Integer)
    label: Mapped[str | None] = mapped_column(String(160), nullable=True)
    content: Mapped[dict] = mapped_column(JSON, default=dict)
    change_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    portfolio = relationship("Portfolio", back_populates="versions")


class PortfolioCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    target_role: str | None = Field(default=None, max_length=160)
    initial_content: dict[str, Any] = Field(default_factory=dict)
    initial_label: str | None = Field(default=None, max_length=160)


class PortfolioVersionCreate(BaseModel):
    content: dict[str, Any]
    label: str | None = Field(default=None, max_length=160)
    change_summary: str | None = Field(default=None, max_length=5000)
