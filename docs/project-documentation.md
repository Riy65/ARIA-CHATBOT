# Aria Portfolio Assistant: Complete Project Documentation

## 1. Project Overview

Aria is a full-stack web application that helps a user turn career information into a structured, reviewable portfolio. The user can create an account, talk with an AI assistant, upload a resume or supporting document, maintain several portfolio workspaces, save immutable portfolio versions, preview or download a standalone HTML portfolio, and evaluate a version with an explainable readiness score.

The application is called a chatbot in some older project files, but the current product is more specific: it is a portfolio-building assistant with chat, document context, profile extraction, portfolio generation, version history, and deterministic assessment.

### Main product goals

- Collect professional information conversationally.
- Reuse information from uploaded resumes and documents.
- Keep conversations and portfolio data private to the authenticated user.
- Generate useful portfolio content without silently inventing facts.
- Preserve earlier portfolio versions when a user saves changes.
- Explain what is strong, missing, or worth improving.
- Export the result as a self-contained HTML page.

## 2. What a User Can Do

### Account and access

1. Create an account with an email address and password.
2. Log in and receive a bearer JWT.
3. Use the token for protected chat, profile, document, portfolio, and assessment operations.
4. Log out by removing the token from browser storage.

### Chat

1. Open the chat page.
2. Aria creates a conversation automatically if the user has no conversations.
3. Send career details, goals, skills, projects, experience, or portfolio requests.
4. Aria receives recent conversation history and relevant stored document context.
5. Conversations can be renamed automatically and deleted by the user.
6. Long conversations retain a compact summary in addition to the latest messages.

### Documents and profile information

1. Upload a PDF, DOCX, or TXT file up to 10 MB.
2. The backend extracts readable text from the file.
3. The extracted text is capped at 24,000 characters.
4. Gemini extracts portfolio-relevant facts into structured JSON.
5. The facts and a text excerpt are retained as document context for later chats.
6. A separate review-only endpoint can extract profile facts from a chat without saving them automatically.
7. The user can explicitly save confirmed profile information through the profile update endpoint.

### Portfolio workspace

1. Create a named portfolio and optionally set a target role.
2. Start with immutable version 1.
3. Edit portfolio content as JSON in the workspace.
4. Save changes as a new version instead of overwriting the previous version.
5. Preview a version in a sandboxed HTML iframe.
6. Download a standalone HTML version.
7. Assess a specific version with the readiness rubric.

## 3. System Architecture

```mermaid
flowchart LR
    Browser[Static HTML CSS JavaScript] -->|Bearer JWT and JSON| API[FastAPI application]
    API --> Auth[JWT and bcrypt authentication]
    API --> Chat[Chat routes]
    API --> Profile[Profile and document routes]
    API --> Portfolio[Portfolio routes]
    API --> Assessment[Assessment routes]
    Chat --> AI[Gemini REST API through requests]
    Profile --> Extract[PDF DOCX TXT extraction]
    Extract --> AI
    API --> ORM[SQLAlchemy ORM]
    ORM --> DB[(PostgreSQL)]
    Portfolio --> Export[Self-contained HTML renderer]
    Assessment --> Rubric[Deterministic scoring service]
```

### Runtime arrangement

The backend is the application host. FastAPI exposes the JSON API and also mounts the `frontend/` directory as static files. In the normal local setup, the browser loads the frontend and sends API requests to the same origin, so no separate frontend development server or build system is required.

The major runtime layers are:

- **Presentation layer:** static HTML, CSS, and browser JavaScript.
- **API layer:** FastAPI routers and request validation.
- **Security layer:** password hashing, JWT creation, JWT verification, and ownership checks.
- **Application layer:** chat orchestration, profile extraction, portfolio generation, export, and scoring.
- **Persistence layer:** SQLAlchemy models and a configured relational database.
- **External AI layer:** Google Gemini accessed through its REST endpoint.

## 4. Repository Structure

```text
ai-chatbot/
├── README.md
├── backend/
│   ├── .env.example
│   ├── ai_client.py
│   ├── database.py
│   ├── main.py
│   ├── requirements.txt
│   ├── requirements-documents.txt
│   ├── schemas.py
│   ├── models/
│   │   ├── chat.py
│   │   ├── portfolio.py
│   │   ├── profile.py
│   │   └── user.py
│   ├── routes/
│   │   ├── assessment.py
│   │   ├── auth.py
│   │   ├── chat.py
│   │   ├── portfolio.py
│   │   └── profile.py
│   ├── services/
│   │   ├── portfolio_export.py
│   │   └── portfolio_scoring.py
│   ├── utils/
│   │   └── auth.py
│   └── private_uploads/
├── docs/
│   ├── portfolio-assistant-data-model.md
│   ├── portfolio-assistant-progress.md
│   └── project-documentation.md
└── frontend/
    ├── index.html
    ├── login.html
    ├── login.js
    ├── portfolio.html
    ├── portfolio.js
    ├── script.js
    ├── signup.html
    ├── signup.js
    └── style.css
```

## 5. Backend Technology Stack

### Python

Python is the backend programming language. It provides the runtime for the API, authentication helpers, database access, document parsing, AI integration, and portfolio services.

### FastAPI

FastAPI is the HTTP API framework used in `backend/main.py` and the route modules.

It provides:

- Route decorators such as `@router.post` and `@router.get`.
- Dependency injection for the current user and database session.
- Request parsing and validation through Pydantic models.
- Automatic OpenAPI documentation.
- Static file mounting for the frontend.
- Middleware support, including CORS.

The application is created as `FastAPI(title="Aria Chatbot API", version="1.0.0")`.

### Uvicorn

Uvicorn is the ASGI server used to run FastAPI locally and in deployment. The development command is:

```bash
cd backend
uvicorn main:app --reload
```

The `--reload` flag watches source files and restarts the server during development.

### SQLAlchemy

SQLAlchemy 2.x is the ORM and database access layer. Models use typed declarative mappings such as `Mapped[str]` and `mapped_column`.

SQLAlchemy is responsible for:

- Mapping Python classes to relational tables.
- Defining foreign keys and relationships.
- Querying with `select()`.
- Creating sessions through `SessionLocal`.
- Enforcing ownership filters in route queries.
- Creating tables at startup through `Base.metadata.create_all(bind=engine)`.

The current project does not show an Alembic migration setup. Schema changes therefore require deliberate database management rather than assuming migrations are available.

### PostgreSQL and psycopg

PostgreSQL is the intended relational database. The connection is supplied through `DATABASE_URL`, for example:

```env
DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/aria
```

The `psycopg` driver allows SQLAlchemy to connect to PostgreSQL. The engine enables `pool_pre_ping=True`, which checks pooled connections before use.

### Pydantic

Pydantic validates incoming API data. Examples include:

- `UserCreate` validates email format and requires a password of at least six characters.
- `ProfileUpdate` validates optional profile fields and URL types.
- `PortfolioCreate` validates portfolio names and JSON content.
- `PortfolioVersionCreate` validates version content and change summaries.
- `ChatRequest` validates a conversation UUID and message length.

### python-dotenv

`python-dotenv` loads variables from `backend/.env` into the process environment. The application uses it for the database URL, JWT signing key, Gemini key, and Gemini model.

### Requests and Google Gemini REST API

The AI integration uses the `requests` library directly rather than a dedicated Gemini SDK. `backend/ai_client.py` builds Gemini REST payloads and sends them to:

```text
https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent
```

The key is read from `GEMINI_API_KEY`, with `GOOGLE_API_KEY` as a fallback. The default model is `gemini-3.6-flash`, configurable through `GEMINI_MODEL`.

Gemini is used for:

- Normal conversational replies.
- Conversation title generation.
- Profile fact extraction from chat.
- Document fact extraction.
- Portfolio draft generation.
- Long-session context summarization.

The request includes system instructions, user and assistant messages, optional document context, and optional context summaries. Structured extraction requests set Gemini's response MIME type to `application/json`.

### Passlib and bcrypt

Passlib's bcrypt scheme hashes passwords before storage. Plain-text passwords are never stored by the application. Login verifies the supplied password against the stored bcrypt hash.

### python-jose and HS256 JWT

`python-jose` creates and verifies JSON Web Tokens. Tokens use the HS256 signing algorithm and expire after 24 hours. The signing key comes from `JWT_SECRET_KEY`.

JWT claims include:

- `sub`: the user's database ID.
- `email`: the user's normalized email address.
- `exp`: the expiration timestamp.

### python-multipart

FastAPI uses `python-multipart` to parse multipart form data for document uploads.

### pypdf

`pypdf` extracts text from PDF pages in memory. The upload route joins extracted page text and applies the application character limit.

### python-docx

`python-docx` reads DOCX files from an in-memory byte stream and extracts paragraph text.

## 6. Frontend Technology Stack

### HTML

The frontend is built from static HTML pages:

- `login.html`: sign-in form.
- `signup.html`: account creation form.
- `index.html`: chat application.
- `portfolio.html`: portfolio workspace.

There is no React, Vue, Angular, TypeScript, JSX, or frontend package manager in the current project.

### CSS

`frontend/style.css` contains the shared visual system. It defines:

- CSS custom properties for colors, spacing-related values, borders, and shadows.
- Authentication layouts.
- Chat sidebar, message bubbles, composer, upload control, and responsive rules.
- Portfolio workspace, editor, assessment card, dialog, and fullscreen preview styles.
- Mobile breakpoints for narrower screens.

The application uses Google Fonts including Fraunces, Space Grotesk, Inter, and JetBrains Mono.

### Browser JavaScript

The frontend uses plain browser JavaScript and the Fetch API.

`login.js`:

- Sends credentials to `/auth/login`.
- Stores the returned JWT and email in `localStorage`.
- Redirects the user to the chat page.

`signup.js`:

- Sends a new email and password to `/auth/signup`.
- Reports validation or API errors.
- Redirects successful registrations to login.

`script.js`:

- Verifies the saved token through `/auth/me`.
- Creates and loads conversations.
- Loads and renders message history.
- Sends chat messages to `/chat/send`.
- Shows a typing indicator.
- Uploads PDF, DOCX, and TXT files.
- Renders assistant Markdown-like output safely.
- Handles conversation deletion, new chats, and logout.

`portfolio.js`:

- Loads and lists portfolios.
- Creates portfolio workspaces.
- Displays the current JSON version in an editor.
- Saves new immutable versions.
- Requests rendered HTML for the preview iframe.
- Downloads standalone HTML.
- Requests and displays portfolio assessments.

The frontend uses `window.ARIA_API_URL || ""`. An empty value means same-origin requests, which is the intended arrangement when FastAPI serves the static files.

## 7. Database Design

### User and ownership model

The `users` table is the root of the ownership tree. A user can own:

- One optional `user_profiles` row.
- Many `chat_sessions`.
- Many `uploaded_files`.
- Many `portfolios`.

Foreign keys use cascading deletes for owned records. Route queries also filter by the authenticated user's ID, preventing a user from addressing another user's records by UUID or numeric ID.

### Tables

#### `users`

Defined in `backend/models/user.py`.

Stores the normalized email, bcrypt password hash, and creation timestamp. Email is unique and indexed.

#### `user_profiles`

Defined in `backend/models/profile.py`.

Stores structured professional information:

- Full name.
- Headline.
- Location.
- Target role.
- Bio.
- LinkedIn URL.
- Website URL.
- Flexible `manual_details` JSON.

There is one profile per user, enforced by a unique `user_id` foreign key.

#### `uploaded_files`

Stores document or professional-link metadata:

- Source type.
- Display title.
- Source URL, when applicable.
- Storage key, reserved for private storage.
- Original filename.
- Content type.
- Size in bytes.
- Extraction status.
- Creation timestamp.

The current upload implementation reads files into memory and does not persist the original bytes to `private_uploads` or an object-storage provider.

#### `document_extractions`

Stores AI-derived document context separately from upload metadata:

- Extracted structured facts as JSON.
- A text excerpt used as later chat context.
- A one-to-one relationship with an uploaded file.

#### `chat_sessions`

Stores a user's conversation title, timestamps, a durable context summary, and the number of messages already folded into that summary.

#### `chat_messages`

Stores the role (`user` or `assistant`), message content, session relationship, and creation timestamp.

#### `portfolios`

Stores the portfolio name, optional target role, owner, and timestamps.

#### `portfolio_versions`

Stores JSON content snapshots. Each version has:

- A portfolio relationship.
- A sequential version number.
- An optional label.
- JSON content.
- An optional change summary.
- A creation timestamp.

A unique constraint prevents duplicate version numbers within one portfolio.

#### `portfolio_assessments`

Stores the result of scoring one exact portfolio version:

- Rubric version.
- Overall score.
- Category scores.
- Strengths.
- Gaps.
- Recommended actions.
- Creation timestamp.

### Versioning behavior

A save never updates an existing `portfolio_versions` row. The backend finds the latest number and inserts the next version. This protects historical content and makes assessments traceable to the exact content that was evaluated.

## 8. API Reference

Protected endpoints require:

```http
Authorization: Bearer <jwt>
```

### Authentication routes

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/auth/signup` | Create a user account. |
| `POST` | `/auth/login` | Verify credentials and return a 24-hour bearer JWT. |
| `GET` | `/auth/me` | Confirm the current token and return the user's email. |

### Chat routes

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/chat/new` | Create an empty user-owned conversation. |
| `POST` | `/chat/send` | Save a user message, assemble context, call Aria, save the reply, and possibly create a portfolio draft. |
| `GET` | `/chat/conversations` | List conversations owned by the current user. |
| `GET` | `/chat/messages/{conversation_id}` | Return messages for an owned conversation. |
| `DELETE` | `/chat/conversation/{conversation_id}` | Delete an owned conversation and its messages. |

### Profile and source routes

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/profile` | Return the current structured profile. |
| `PUT` | `/profile` | Create or update profile fields explicitly. |
| `POST` | `/profile/sources` | Save a professional URL as source metadata. |
| `GET` | `/profile/sources` | List saved URLs and uploaded-file metadata. |
| `POST` | `/profile/uploads` | Extract facts from a PDF, DOCX, or TXT upload. |
| `POST` | `/profile/drafts/from-chat/{conversation_id}` | Return a review-only profile draft from user messages. |

### Portfolio routes

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/portfolios` | Create a portfolio and version 1. |
| `GET` | `/portfolios` | List the user's portfolios. |
| `GET` | `/portfolios/{portfolio_id}` | Return a portfolio and its versions. |
| `POST` | `/portfolios/{portfolio_id}/versions` | Create the next immutable version. |
| `GET` | `/portfolios/{portfolio_id}/versions/{version_id}/render` | Return authenticated standalone HTML for preview. |
| `GET` | `/portfolios/{portfolio_id}/versions/{version_id}/download` | Return the same HTML with download headers. |

### Assessment routes

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/portfolios/{portfolio_id}/versions/{version_id}/assess` | Score and persist an exact portfolio version. |
| `GET` | `/portfolios/{portfolio_id}/versions/{version_id}/assessments` | List previous assessments for that version. |

## 9. Chat Processing Flow

When the user sends a message, `routes/chat.py` performs the following sequence:

1. Resolve the authenticated database user from the JWT email claim.
2. Find the requested conversation while checking ownership.
3. Save the trimmed user message.
4. Load up to the latest 20 messages and restore chronological order.
5. Add the Aria system instruction.
6. Add up to three recent completed document extractions.
7. Add the durable context summary, if one exists.
8. Send the assembled messages to `get_ai_reply()`.
9. Save the assistant reply.
10. Generate a first conversation title when the conversation still has its default title.
11. Summarize newly overflowed messages when the conversation exceeds the recent-message window.
12. Commit the transaction and return the reply and title.

The system prompt asks Aria to be concise, ask focused follow-up questions, and give practical portfolio recommendations. Document context is explicitly described as factual context, and prompts instruct the model to ignore instructions embedded inside uploaded documents.

### Long-session context

The latest 20 messages remain verbatim in each normal AI request. When older messages fall outside that window, only newly overflowed messages are summarized and added to `chat_sessions.context_summary`. `context_message_count` prevents the same old messages from being summarized repeatedly.

## 10. AI Behavior and Fallbacks

`backend/ai_client.py` isolates AI communication from the route layer.

### Normal replies

`get_ai_reply()` calls Gemini with a maximum output token budget of 1,000. If the call fails for any reason, it logs a warning and returns the local fallback from `local_portfolio_reply()`.

The current fallback is intentionally simple and does not generate a unique AI answer. If the UI repeatedly displays the same generic sentence, likely causes include:

- `GEMINI_API_KEY` is missing.
- The Gemini model name is invalid or unavailable.
- The API request is rejected.
- Network access or timeout failure occurs.
- The backend was started before environment variables were updated.

The warning logged by the backend contains the underlying failure reason.

### Structured extraction

Profile and document extraction requests ask Gemini for only supported JSON fields and explicitly prohibit inference or embellishment. The application filters returned data to supported profile fields before returning or storing it.

### Portfolio generation

When chat contains an explicit request to create, build, generate, or make a portfolio, the backend gathers the user's chat details and document context. Gemini is asked for a portfolio name, target role, and JSON content. A deterministic starter structure is used if generation fails.

## 11. Document Processing

The upload route accepts only `.pdf`, `.docx`, and `.txt` extensions and applies a 10 MB byte limit.

Processing steps:

1. Sanitize the filename to its basename.
2. Read the upload into memory.
3. Reject unsupported extensions or oversized files.
4. Extract text with the format-specific parser.
5. Reject documents with no readable text.
6. Truncate extracted text to 24,000 characters.
7. Create an upload metadata row with `processing` status.
8. Send the text to Gemini for factual portfolio extraction.
9. Store extracted facts and the capped context excerpt.
10. Mark the upload `completed`, or `failed` if extraction fails.

The original file bytes are not currently retained. The `storage_key` field and `private_uploads` directory indicate a future private-storage design, but the active route does not write files there.

Professional links are saved as metadata with `pending` status. The current implementation does not fetch or parse the linked page.

## 12. Portfolio HTML Rendering

`backend/services/portfolio_export.py` creates a self-contained HTML document. It embeds all CSS in the generated page, so the downloaded file does not depend on the Aria application being online.

Supported standard sections include:

- About, bio, or summary.
- Skills.
- Projects.
- Experience.
- Education.
- Certifications.
- Achievements.
- Contact and links.

Unknown JSON keys are also rendered as titled sections. Dictionaries and lists become nested HTML lists. All user-controlled values pass through `html.escape()` before insertion.

The workspace preview loads the generated HTML into a sandboxed iframe. The preview dialog is fullscreen in the application UI, while the generated portfolio keeps an internal readable content width of approximately 850 pixels.

## 13. Portfolio Scoring

`backend/services/portfolio_scoring.py` applies a deterministic rubric with a maximum score of 100:

| Category | Maximum |
|---|---:|
| Completeness | 20 |
| Impact evidence | 20 |
| Skills clarity | 15 |
| Project depth | 15 |
| Experience depth | 15 |
| Target-role alignment | 15 |
| **Total** | **100** |

The scorer looks for structured sections, text content, target-role information, and numeric evidence such as percentages, quantities, users, clients, time, or scale. It returns category scores, strengths, gaps, and up to five recommended actions.

Because scoring is deterministic, identical content and target-role data produce the same result. The rubric version is stored with each assessment so future rubric changes can be distinguished from earlier results.

## 14. Local Setup

### Prerequisites

- Python 3.13 or a compatible supported Python version.
- PostgreSQL running locally or a reachable PostgreSQL database.
- A Gemini API key for live AI behavior.
- Git, if cloning the project.

### Create and activate a virtual environment

Windows PowerShell example:

```powershell
cd c:\path\to\ai-chatbot\backend
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Install dependencies

```powershell
pip install -r requirements.txt
```

The separate document dependency file is:

```powershell
pip install -r requirements-documents.txt
```

`requirements.txt` should be the normal complete installation. The document file is useful when installing or checking only PDF and DOCX support.

### Configure environment variables

Create `backend/.env` using `backend/.env.example` as a starting point:

```env
DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/aria
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3.6-flash
JWT_SECRET_KEY=replace_with_a_long_random_secret
```

Use a long random value for `JWT_SECRET_KEY`. Do not commit `.env` or any API key.

### Start the application

```powershell
cd backend
uvicorn main:app --reload
```

Open:

```text
http://127.0.0.1:8000/login.html
```

FastAPI serves both the API and static frontend from this address. The API's automatic documentation is normally available at `/docs`.

## 15. Configuration and Current-State Notes

This section is important because some older project documents describe earlier implementations.

- The current AI client calls Google Gemini through HTTP. Older README and progress text still refer to OpenAI.
- `OPENAI_API_KEY` may still appear in `.env.example`, but the current chat implementation uses `GEMINI_API_KEY` or `GOOGLE_API_KEY`.
- The current `database.py` raises an error when `DATABASE_URL` is missing. Do not rely on older documentation that promises an automatic SQLite fallback.
- The repository contains a local `aria.db`, but the active database engine is configured from `DATABASE_URL`.
- The current source uses PostgreSQL and SQLAlchemy, not MongoDB.
- The current upload route extracts content and stores extracted context in the database; it does not yet implement private object storage for original files.
- No Alembic migrations are visible in the repository.
- The frontend has no npm install, bundling, or compile step.

## 16. Security and Privacy Considerations

Implemented protections:

- Passwords are bcrypt-hashed.
- Protected routes require a JWT.
- Database queries check authenticated ownership.
- Uploaded file types and sizes are restricted.
- Portfolio HTML values are escaped before rendering.
- Preview HTML is placed in a sandboxed iframe.
- Uploaded document prompts tell the model to ignore embedded instructions.

Current risks and limitations:

- JWTs are stored in browser `localStorage`, which increases exposure if a future XSS issue is introduced.
- There is no refresh-token flow, password reset, email verification, rate limiting, or strong password policy beyond six characters.
- CORS allows broad methods and headers for configured origins.
- Original document bytes are read into memory and are not stored in private object storage.
- A production deployment should use database migrations, structured logging, secret rotation, stricter CORS, upload scanning, rate limits, and an appropriate token storage strategy.
- Frontend conversation titles should be escaped before being inserted into `innerHTML`.

## 17. Recommended Development Workflow

1. Start PostgreSQL and verify `DATABASE_URL`.
2. Activate the backend virtual environment.
3. Install or update `requirements.txt`.
4. Confirm `.env` contains a valid JWT secret and Gemini key.
5. Run Uvicorn from `backend/`.
6. Test signup and login first.
7. Test a chat message and inspect backend logs if the response is the local fallback.
8. Test a document upload with a small readable file.
9. Create a portfolio and save a second version.
10. Preview and download the generated HTML.
11. Assess a version and verify that the result is tied to that version.

For frontend-only changes, use browser developer tools and refresh the static page. There is no frontend build command.

## 18. Future Improvements

The project structure supports several natural next steps:

- Replace direct `requests` calls with a managed AI client or add retry and error classification.
- Add an explicit AI provider health endpoint and a visible fallback status in the UI.
- Add streaming assistant responses.
- Add profile and source-management screens.
- Fetch and process professional links with consent and safe network controls.
- Move original files to private object storage with signed URLs.
- Add Alembic migrations.
- Add automated backend and browser tests.
- Improve Markdown rendering with a vetted sanitizer or a controlled Markdown library.
- Escape all dynamic frontend values before assigning `innerHTML`.
- Add rate limiting, password reset, email verification, refresh tokens, and stronger password rules.
- Add deployment configuration and observability.

## 19. Key Files at a Glance

| File | Responsibility |
|---|---|
| `backend/main.py` | Creates FastAPI app, middleware, routers, startup table creation, and static frontend mount. |
| `backend/database.py` | Loads database configuration and creates SQLAlchemy engine/session helpers. |
| `backend/ai_client.py` | Calls Gemini, generates replies/titles, extracts facts, generates drafts, and summarizes context. |
| `backend/utils/auth.py` | Hashes passwords and creates/verifies JWTs. |
| `backend/routes/auth.py` | Signup, login, and token verification endpoints. |
| `backend/routes/chat.py` | Conversation creation, message handling, context assembly, and history. |
| `backend/routes/profile.py` | Profiles, professional links, uploads, document extraction, and chat profile drafts. |
| `backend/routes/portfolio.py` | Portfolio workspaces, immutable versions, HTML rendering, and downloads. |
| `backend/routes/assessment.py` | Version assessment creation and history. |
| `backend/services/portfolio_export.py` | Escaped standalone HTML portfolio generation. |
| `backend/services/portfolio_scoring.py` | Explainable deterministic 100-point rubric. |
| `frontend/script.js` | Chat UI and browser-side chat workflow. |
| `frontend/portfolio.js` | Portfolio workspace and preview workflow. |
| `frontend/style.css` | Shared visual design and responsive layout. |

## 20. Summary

Aria is currently a static-frontend plus FastAPI application backed by SQLAlchemy and PostgreSQL. Its central workflow is:

```text
Authenticate -> chat or upload evidence -> assemble factual context -> generate portfolio content -> save immutable versions -> preview/download -> score and improve
```

Gemini provides natural-language generation and structured extraction, while the portfolio renderer and scoring service remain deterministic application code. This separation makes the product flexible for conversation while keeping exported HTML, version history, ownership checks, and scoring behavior controlled by the backend.
