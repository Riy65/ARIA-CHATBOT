from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from database import get_db
from models.portfolio import Portfolio, PortfolioCreate, PortfolioVersion, PortfolioVersionCreate
from services.portfolio_export import render_portfolio_html
from models.user import User
from utils.auth import get_current_user

router = APIRouter()


def current_db_user(db: Session, claims: dict) -> User:
    user = db.scalar(select(User).where(User.email == claims["email"]))
    if not user:
        raise HTTPException(status_code=401, detail="User account no longer exists")
    return user


def owned_portfolio(db: Session, portfolio_id: UUID, user_id: int) -> Portfolio:
    portfolio = db.scalar(select(Portfolio).where(Portfolio.id == portfolio_id, Portfolio.user_id == user_id))
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return portfolio


def serialize_version(version: PortfolioVersion) -> dict:
    return {"version_id": str(version.id), "version_number": version.version_number, "label": version.label, "content": version.content or {}, "change_summary": version.change_summary, "created_at": version.created_at}


def serialize_portfolio(portfolio: Portfolio, include_versions: bool = False) -> dict:
    result = {"portfolio_id": str(portfolio.id), "name": portfolio.name, "target_role": portfolio.target_role, "created_at": portfolio.created_at, "updated_at": portfolio.updated_at, "version_count": len(portfolio.versions)}
    if include_versions:
        result["versions"] = [serialize_version(version) for version in portfolio.versions]
    return result


@router.post("", status_code=201)
def create_portfolio(payload: PortfolioCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    user = current_db_user(db, current_user)
    portfolio = Portfolio(user_id=user.id, name=payload.name.strip(), target_role=payload.target_role)
    db.add(portfolio)
    db.flush()
    db.add(PortfolioVersion(portfolio_id=portfolio.id, version_number=1, label=payload.initial_label or "Initial version", content=payload.initial_content))
    db.commit()
    db.refresh(portfolio)
    return serialize_portfolio(portfolio, include_versions=True)


@router.get("")
def list_portfolios(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    user = current_db_user(db, current_user)
    portfolios = db.scalars(select(Portfolio).where(Portfolio.user_id == user.id).order_by(desc(Portfolio.updated_at))).all()
    return [serialize_portfolio(portfolio) for portfolio in portfolios]


@router.get("/{portfolio_id}")
def get_portfolio(portfolio_id: UUID, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    user = current_db_user(db, current_user)
    return serialize_portfolio(owned_portfolio(db, portfolio_id, user.id), include_versions=True)


@router.post("/{portfolio_id}/versions", status_code=201)
def create_portfolio_version(portfolio_id: UUID, payload: PortfolioVersionCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    user = current_db_user(db, current_user)
    portfolio = owned_portfolio(db, portfolio_id, user.id)
    latest_number = db.scalar(select(PortfolioVersion.version_number).where(PortfolioVersion.portfolio_id == portfolio.id).order_by(desc(PortfolioVersion.version_number)).limit(1)) or 0
    version = PortfolioVersion(portfolio_id=portfolio.id, version_number=latest_number + 1, label=payload.label, content=payload.content, change_summary=payload.change_summary)
    db.add(version)
    portfolio.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(version)
    return serialize_version(version)


def portfolio_version_for_user(db: Session, portfolio_id: UUID, version_id: UUID, user_id: int) -> tuple[Portfolio, PortfolioVersion]:
    portfolio = owned_portfolio(db, portfolio_id, user_id)
    version = db.scalar(select(PortfolioVersion).where(PortfolioVersion.id == version_id, PortfolioVersion.portfolio_id == portfolio.id))
    if not version:
        raise HTTPException(status_code=404, detail="Portfolio version not found")
    return portfolio, version


@router.get("/{portfolio_id}/versions/{version_id}/render", response_class=HTMLResponse)
def render_portfolio_version(portfolio_id: UUID, version_id: UUID, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    user = current_db_user(db, current_user)
    portfolio, version = portfolio_version_for_user(db, portfolio_id, version_id, user.id)
    return render_portfolio_html(portfolio.name, portfolio.target_role, version.version_number, version.content)


@router.get("/{portfolio_id}/versions/{version_id}/download", response_class=HTMLResponse)
def download_portfolio_version(portfolio_id: UUID, version_id: UUID, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    user = current_db_user(db, current_user)
    portfolio, version = portfolio_version_for_user(db, portfolio_id, version_id, user.id)
    filename = "".join(character if character.isalnum() else "-" for character in portfolio.name.lower()).strip("-") or "portfolio"
    return HTMLResponse(render_portfolio_html(portfolio.name, portfolio.target_role, version.version_number, version.content), headers={"Content-Disposition": f'attachment; filename="{filename}-v{version.version_number}.html"'})
