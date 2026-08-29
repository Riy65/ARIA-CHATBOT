# Aria Portfolio Assistant — Project Tracker

Last updated: 2026-08-29

## Product goal

Evolve Aria from a general-purpose chatbot into a guided portfolio-building assistant. A user should be able to enter their experience manually in chat, provide professional links or upload supporting documents, receive structured feedback, understand their portfolio readiness score, and keep multiple versions of their portfolio over time.

## Working agreement

1. Work is completed one task at a time.
2. Each task is summarized for approval before the next functional task begins.
3. This tracker is updated when a task starts and again when it is completed.
4. Work is performed on the `codex/portfolio-assistant` branch.

## Requirements and status

| Requirement | Status | Notes |
|---|---|---|
| Dedicated feature branch | Complete | `codex/portfolio-assistant` |
| Professional, convenient interface | In progress | Authentication and chat foundation refreshed; profile and portfolio screens remain. |
| Session history and same-session awareness | Foundation complete | User-owned sessions persist; the assistant receives the latest 20 messages from that session. Long-session summaries are planned. |
| User registration and profile data | Foundation complete | Account and user-owned structured profile fields are stored in PostgreSQL. |
| Manual chat-based data collection | Foundation complete | A user-owned chat session can generate a review-only structured profile draft; saving requires confirmation. |
| CV/resume/LinkedIn/document input | In progress | Professional links and document metadata are stored; private file storage and extraction remain. |
| Portfolio data and versions | Foundation complete | User-owned workspaces start with version 1; every later save creates a separate immutable version. |
| Standards-based strength score | Planned | A fixed, explainable rubric will be implemented after the portfolio data model. |
| Existing MongoDB data migration | Planned | No existing data is migrated automatically. |

## Completed work

### Task 1 — Portfolio assistant frontend foundation

Status: Complete and committed in `993b7ee`.

- Created the feature branch.
- Redesigned login, signup, and chat pages for the portfolio-assistant experience.
- Preserved existing frontend API behavior.
- Added the [data model blueprint](portfolio-assistant-data-model.md).

### Task 2 — PostgreSQL session and chat foundation

Status: Complete; pending commit.

- Replaced MongoDB collection access with SQLAlchemy models for users, chat sessions, and messages.
- Added user-owned session authorization for every chat operation.
- Preserved full chat history and supplied the latest 20 same-session messages to the model.
- Added `context_summary` for the later long-session context feature.
- Added PostgreSQL configuration and dependencies.
- Validated the relational models using an in-memory database.

### Task 3 — User profile and document-input foundation

Status: Complete and committed in `123a3b3`.

- Added a user-owned profile API for name, headline, location, target role, bio, LinkedIn URL, website URL, and manual details.
- Added APIs to save and list professional links, such as a LinkedIn profile or hosted resume.
- Added document metadata fields for future uploads, including private storage key, content type, size, and extraction status.
- File contents remain out of the database; private object-storage integration will follow once a provider is selected.

### Task 4 — Structured profile extraction with user confirmation

Status: Complete; pending approval and commit.

- Added `POST /profile/drafts/from-chat/{conversation_id}` for user-owned conversation extraction.
- The extraction prompt accepts only explicit user-provided facts and filters its output to supported profile fields.
- The endpoint returns a review-only draft with `confirmation_required: true`; it never writes to the profile.
- The existing `PUT /profile` endpoint remains the explicit confirmation and save step.
- Verified with a mocked local end-to-end test that confirmed the draft does not change the profile before confirmation.

### Task 5 — Portfolio workspace and immutable versions

Status: Complete; pending approval and commit.

- Added user-owned portfolio workspaces with a name and optional target role.
- Every portfolio starts with an immutable version 1, and every later save creates a new sequential version.
- Added APIs to create, list, inspect, and add a version to portfolios.
- Verified locally that version 2 does not overwrite the original version content.

## Current technical baseline

- API: FastAPI.
- Database: PostgreSQL through SQLAlchemy and `psycopg`.
- AI: OpenAI chat completions.
- Authentication: bcrypt password hashes and 24-hour JWTs.
- Frontend: static HTML, CSS, and JavaScript.
- Files: not yet stored; the target approach is private object storage with short-lived download URLs.

## Planned task sequence

1. User profile and document-input foundation.
2. Structured data extraction and user confirmation from chat/documents.
3. Portfolio workspace, sections, and immutable version history.
4. Explainable portfolio-strength scoring rubric and improvement plan.
5. Long-session context summarization and context retrieval.
6. Professional portfolio dashboard and remaining frontend flows.
7. PostgreSQL migration workflow, security hardening, and deployment preparation.

## Configuration needed before deployment

- Provision a PostgreSQL database and set `DATABASE_URL`.
- Set a strong `JWT_SECRET_KEY`.
- Set `OPENAI_API_KEY`.
- Choose a private object-storage provider before enabling document uploads.
