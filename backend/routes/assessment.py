from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from database import get_db
from models.portfolio import Portfolio, PortfolioAssessment, PortfolioVersion
from models.user import User
from services.portfolio_scoring import score_portfolio
from utils.auth import get_current_user

router = APIRouter()


def current_db_user(db: Session, claims: dict) -> User:
    user = db.scalar(select(User).where(User.email == claims["email"]))
    if not user:
        raise HTTPException(status_code=401, detail="User account no longer exists")
    return user


def owned_version(db: Session, portfolio_id: UUID, version_id: UUID, user_id: int) -> tuple[Portfolio, PortfolioVersion]:
    portfolio = db.scalar(select(Portfolio).where(Portfolio.id == portfolio_id, Portfolio.user_id == user_id))
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    version = db.scalar(select(PortfolioVersion).where(PortfolioVersion.id == version_id, PortfolioVersion.portfolio_id == portfolio.id))
    if not version:
        raise HTTPException(status_code=404, detail="Portfolio version not found")
    return portfolio, version


def serialize_assessment(assessment: PortfolioAssessment) -> dict:
    return {"assessment_id": str(assessment.id), "rubric_version": assessment.rubric_version, "overall_score": assessment.overall_score, "category_scores": assessment.category_scores, "strengths": assessment.strengths, "gaps": assessment.gaps, "recommended_actions": assessment.recommended_actions, "created_at": assessment.created_at}


@router.post("/{portfolio_id}/versions/{version_id}/assess", status_code=201)
def assess_portfolio_version(portfolio_id: UUID, version_id: UUID, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    user = current_db_user(db, current_user)
    portfolio, version = owned_version(db, portfolio_id, version_id, user.id)
    result = score_portfolio(version.content, portfolio.target_role)
    assessment = PortfolioAssessment(portfolio_version_id=version.id, **result)
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return serialize_assessment(assessment)


@router.get("/{portfolio_id}/versions/{version_id}/assessments")
def list_assessments(portfolio_id: UUID, version_id: UUID, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    user = current_db_user(db, current_user)
    _, version = owned_version(db, portfolio_id, version_id, user.id)
    assessments = db.scalars(select(PortfolioAssessment).where(PortfolioAssessment.portfolio_version_id == version.id).order_by(desc(PortfolioAssessment.created_at))).all()
    return [serialize_assessment(assessment) for assessment in assessments]
