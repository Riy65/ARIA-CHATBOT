# Portfolio Assistant: Data Model Blueprint

This is the proposed database plan for the next task. It is designed for PostgreSQL with SQLAlchemy and Alembic.

## Core entities

| Entity | Purpose | Key relationships |
|---|---|---|
| `users` | Authentication identity and account metadata. | Owns sessions, files, and portfolios. |
| `user_profiles` | Structured personal data, such as name, headline, location, links, target roles, and preferences. | One current profile per user; updated from chat or forms. |
| `chat_sessions` | A named, user-owned conversation with retained context. | Has many messages and can be linked to a portfolio. |
| `chat_messages` | Ordered user and assistant messages, plus optional structured extraction results. | Belongs to one chat session. |
| `uploaded_files` | Metadata for CVs, resumes, certificates, and other uploads. Actual bytes live in private object storage. | Belongs to a user; may be referenced in messages and portfolio versions. |
| `portfolio_profiles` | A user’s portfolio workspace (for example, “Product Designer 2026”). | Has many immutable versions and assessments. |
| `portfolio_versions` | A saved portfolio snapshot containing sections and source-data references. | Belongs to a portfolio profile. |
| `portfolio_assessments` | Explainable portfolio score and rubric category results. | Belongs to a portfolio version. |

## Context and continuity

Each `chat_session` will store a compact `context_summary` and `last_active_at`. Full messages remain in `chat_messages`; the assistant receives the summary plus the most recent relevant messages. This maintains continuity while keeping AI prompts efficient.

Structured facts discovered in chat, such as work history or skills, require the user’s confirmation before promotion into `user_profiles` or a portfolio version.

## Files and privacy

Files should use private object storage. The database stores the file name, MIME type, size, private storage key, upload timestamp, processing status, and extracted-text reference. Downloads should use short-lived signed URLs.

## Portfolio versions and scoring

Saving a portfolio creates an immutable `portfolio_versions` record rather than overwriting prior work. Each assessment uses a fixed rubric: completeness, evidence of impact, skills clarity, project depth, experience, readability, and target-role alignment. The resulting overall score, category scores, strengths, gaps, and recommended actions are stored with that version.
