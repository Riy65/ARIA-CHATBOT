from html import escape
from typing import Any


SECTION_LABELS = {
    "about": "About", "bio": "About", "summary": "About", "skills": "Skills",
    "projects": "Projects", "experience": "Experience", "education": "Education",
    "certifications": "Certifications", "achievements": "Achievements", "contact": "Contact", "links": "Links",
}


def display_value(value: Any) -> str:
    if isinstance(value, dict):
        items = "".join(f"<li><strong>{escape(str(key).replace('_', ' ').title())}:</strong> {display_value(item)}</li>" for key, item in value.items() if item not in (None, "", [], {}))
        return f"<ul>{items}</ul>" if items else ""
    if isinstance(value, list):
        items = "".join(f"<li>{display_value(item)}</li>" for item in value if item not in (None, "", [], {}))
        return f"<ul>{items}</ul>" if items else ""
    return escape(str(value))


def render_portfolio_html(name: str, target_role: str | None, version_number: int, content: dict[str, Any]) -> str:
    """Return a self-contained, safely escaped portfolio page for one saved version."""
    content = content or {}
    headline = content.get("headline") or target_role or "Professional portfolio"
    intro = content.get("about") or content.get("bio") or content.get("summary") or ""
    sections = []
    seen = set()
    for key, label in SECTION_LABELS.items():
        canonical = "about" if key in {"bio", "summary"} else key
        if canonical in seen or key not in content or content[key] in (None, "", [], {}):
            continue
        seen.add(canonical)
        sections.append(f"<section><h2>{escape(label)}</h2><div class=\"section-content\">{display_value(content[key])}</div></section>")
    for key, value in content.items():
        if key in SECTION_LABELS or value in (None, "", [], {}):
            continue
        sections.append(f"<section><h2>{escape(str(key).replace('_', ' ').title())}</h2><div class=\"section-content\">{display_value(value)}</div></section>")
    body = "\n".join(sections) or "<section><h2>Portfolio in progress</h2><p>Add your summary, projects, experience, and skills in Aria to build this page.</p></section>"
    return f"""<!doctype html>
<html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>{escape(name)}</title>
<style>body{{background:#f7f8f6;color:#1b2923;font:16px/1.65 Arial,sans-serif;margin:0}}main{{background:#fff;box-shadow:0 12px 40px #1b29231a;margin:40px auto;max-width:850px;padding:clamp(28px,7vw,72px)}}header{{border-bottom:1px solid #dbe2dc;margin-bottom:38px;padding-bottom:28px}}h1{{font-size:clamp(34px,6vw,58px);letter-spacing:-.05em;line-height:1.05;margin:0 0 12px}}.headline{{color:#157a5a;font-weight:700;margin:0}}.intro{{color:#4a5b52;max-width:680px}}section{{margin:34px 0}}h2{{font-size:21px;letter-spacing:-.02em;margin:0 0 13px}}ul{{padding-left:22px}}li{{margin:7px 0}}strong{{color:#0d5c43}}footer{{border-top:1px solid #dbe2dc;color:#68736d;font-size:12px;margin-top:44px;padding-top:18px}}</style></head>
<body><main><header><h1>{escape(name)}</h1><p class=\"headline\">{escape(str(headline))}</p>{f'<p class=\"intro\">{escape(str(intro))}</p>' if intro else ''}</header>{body}<footer>Created with Aria · Version {version_number}</footer></main></body></html>"""
