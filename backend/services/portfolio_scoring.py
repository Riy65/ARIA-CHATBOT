import re
from typing import Any


RUBRIC_VERSION = "1.0"


def as_list(value: Any) -> list:
    return value if isinstance(value, list) else []


def text_for(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return " ".join(text_for(item) for item in value.values())
    if isinstance(value, list):
        return " ".join(text_for(item) for item in value)
    return ""


def contains_evidence(value: Any) -> bool:
    return bool(re.search(r"\b\d+(?:[,.]\d+)?(?:%|\+|x| users| clients| days| months| years)?\b", text_for(value), re.IGNORECASE))


def score_portfolio(content: dict[str, Any], target_role: str | None = None) -> dict:
    """Apply a deterministic, explainable 100-point portfolio rubric."""
    content = content or {}
    skills = as_list(content.get("skills"))
    projects = as_list(content.get("projects"))
    experience = as_list(content.get("experience"))
    education = as_list(content.get("education"))
    about = text_for(content.get("about") or content.get("bio") or content.get("summary"))
    contact = text_for(content.get("contact") or content.get("links"))
    evidence_items = projects + experience

    categories = {
        "completeness": min(20, (5 if about else 0) + (4 if skills else 0) + (4 if projects else 0) + (4 if experience else 0) + (3 if education or contact else 0)),
        "impact_evidence": min(20, 10 if any(contains_evidence(item) for item in experience) else 0) + min(10, sum(1 for item in evidence_items if contains_evidence(item)) * 3),
        "skills_clarity": min(15, len(skills) * 2 + (3 if any(isinstance(item, dict) and item.get("level") for item in skills) else 0)),
        "project_depth": min(15, len(projects) * 4 + sum(1 for item in projects if text_for(item).strip()) * 2),
        "experience_depth": min(15, len(experience) * 5 + sum(1 for item in experience if text_for(item).strip()) * 2),
        "role_alignment": 15 if target_role and (about or projects or experience) else (8 if target_role else 0),
    }
    total = min(100, sum(categories.values()))
    strengths = []
    gaps = []
    actions = []

    if categories["skills_clarity"] >= 10:
        strengths.append("Skills are clearly represented.")
    else:
        gaps.append("Skills are missing or too limited.")
        actions.append("Add a focused skills section with your strongest, role-relevant tools and technologies.")
    if categories["project_depth"] >= 10:
        strengths.append("Projects provide useful evidence of your work.")
    else:
        gaps.append("Projects need more detail or are missing.")
        actions.append("Add 2–3 projects with your role, decisions, outcomes, and links where possible.")
    if categories["impact_evidence"] >= 12:
        strengths.append("The portfolio includes measurable evidence of impact.")
    else:
        gaps.append("Achievements lack measurable outcomes.")
        actions.append("Add specific outcomes to experience and projects, such as percentage improvements, scale, time saved, or users served.")
    if categories["role_alignment"] >= 12:
        strengths.append("The content is aligned with a stated target role.")
    else:
        gaps.append("Target-role alignment is unclear.")
        actions.append("Set a target role and tailor your headline, summary, skills, and selected projects to it.")
    if categories["completeness"] < 14:
        gaps.append("Core portfolio sections are incomplete.")
        actions.append("Complete your summary, experience, projects, skills, education, and contact or professional links.")
    if not strengths:
        strengths.append("This version provides a starting point for structured improvement.")

    return {
        "rubric_version": RUBRIC_VERSION,
        "overall_score": total,
        "category_scores": categories,
        "strengths": strengths,
        "gaps": gaps,
        "recommended_actions": actions[:5],
    }
