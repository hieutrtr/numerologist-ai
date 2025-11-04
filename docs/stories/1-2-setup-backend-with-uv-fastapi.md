# Story 1.2: Setup Backend with uv & FastAPI

**Status:** review

**Story ID:** 1.2

**Epic:** 1 - Foundation & Project Setup

---

## Story

**As a** backend developer,
**I want** a uv-managed FastAPI project with fast dependency management,
**so that** I can start building API endpoints with a solid foundation.

---

## Acceptance Criteria

1. `backend/` folder initialized with uv (`uv init`)
2. `pyproject.toml` configured with FastAPI, Uvicorn, SQLModel, Alembic
3. Dependencies organized: main dependencies + optional dev dependencies
4. `src/` folder structure created: `main.py`, `api/`, `core/`, `models/`, `services/`
5. Basic FastAPI app in `src/main.py` with root endpoint
6. `uv sync` installs all dependencies successfully
7. `uv run uvicorn src.main:app --reload` starts server at localhost:8000
8. Visiting `http://localhost:8000` returns `{"message": "Numerologist AI API"}`
9. API docs available at `http://localhost:8000/docs`

---

## Tasks / Subtasks

- [x] **Task 1: Initialize uv project** (AC: #1)
  - [x] Navigate to backend directory
  - [x] Run `uv init` in backend folder
  - [x] Verify `pyproject.toml` and `.python-version` are created

- [x] **Task 2: Configure dependencies in pyproject.toml** (AC: #2, #3)
  - [x] Add main dependencies: FastAPI (>=0.109.0), Uvicorn[standard] (>=0.27.0), SQLModel (>=0.0.14), Alembic (>=1.13.0), Pydantic (>=2.5.0), python-jose[cryptography] (>=3.3.0), bcrypt (>=4.1.0), redis (>=5.0.0)
  - [x] Add dev dependencies: pytest (>=7.4.0), black (>=24.1.0), ruff (>=0.1.0)
  - [x] Verify `requires-python = ">=3.10"` is set
  - [x] Update project metadata: name="numerologist-api", version="0.1.0", description="Numerologist AI Backend"

- [x] **Task 3: Create source folder structure** (AC: #4)
  - [x] Create `src/` directory inside backend/
  - [x] Create `src/api/` directory
  - [x] Create `src/core/` directory
  - [x] Create `src/models/` directory
  - [x] Create `src/services/` directory
  - [x] Create `src/__init__.py` for Python package

- [x] **Task 4: Implement basic FastAPI app** (AC: #5)
  - [x] Create `src/main.py` with FastAPI app instance
  - [x] Add root endpoint that returns `{"message": "Numerologist AI API"}`
  - [x] Configure CORS middleware for frontend integration
  - [x] Add startup/shutdown event handlers

- [x] **Task 5: Install dependencies** (AC: #6)
  - [x] Run `uv sync` in backend directory
  - [x] Verify all dependencies are installed without errors
  - [x] Check `.venv` directory is created

- [x] **Task 6: Test FastAPI server** (AC: #7, #8, #9)
  - [x] Start server with `uv run uvicorn src.main:app --reload`
  - [x] Verify server starts on localhost:8000
  - [x] Test root endpoint with curl/browser: `http://localhost:8000`
  - [x] Verify response: `{"message": "Numerologist AI API"}`
  - [x] Access API docs at `http://localhost:8000/docs`
  - [x] Verify Swagger UI loads successfully

- [x] **Task 7: Commit to Git** (Supporting)
  - [x] Stage backend/ directory and story files
  - [x] Create commit with message: "Story 1.2: Setup Backend with uv & FastAPI"
  - [x] Pushed to repository (commit: d95adf7)

---

## Dev Notes

### Architecture Context

- **Backend Framework**: FastAPI for modern, fast API development with automatic OpenAPI docs
- **Package Manager**: uv provides fast, deterministic dependency resolution compared to pip/poetry
- **Database Preparation**: SQLModel (SQLAlchemy + Pydantic) for ORM; Alembic for migrations (used in Story 1.5)
- **Authentication Prep**: python-jose and bcrypt dependencies added for future auth implementation (Story 2)
- **Caching Prep**: redis dependency added for future caching (Stories 6, 8)

Source: [docs/epics.md#Story-1.2-Setup-Backend-with-uv-FastAPI]

### Project Structure

```
numerologist-ai/
├── backend/                          # ← This story populates this
│   ├── pyproject.toml                # uv config + dependencies
│   ├── .python-version               # Python version specification
│   ├── .venv/                        # Virtual environment (created by uv sync)
│   └── src/                          # Source code root
│       ├── __init__.py               # Python package marker
│       ├── main.py                   # FastAPI app entry point
│       ├── api/                      # API routes (populated in later stories)
│       ├── core/                     # Core utilities (config, exceptions, etc)
│       ├── models/                   # SQLModel ORM models
│       └── services/                 # Business logic services
├── mobile/                           # React Native (Story 1.3)
└── Makefile                          # Commands reference (Story 1.7)
```

### Key Dependencies & Versions

- **fastapi (>=0.109.0)**: Web framework with automatic OpenAPI schema generation
- **uvicorn[standard] (>=0.27.0)**: ASGI server with hot reload support
- **sqlmodel (>=0.0.14)**: SQLAlchemy ORM + Pydantic validation (hybrid approach)
- **alembic (>=1.13.0)**: Database migration tool (initialized in Story 1.5)
- **pydantic (>=2.5.0)**: Data validation library (already in fastapi, explicitly included)
- **python-jose[cryptography] (>=3.3.0)**: JWT token creation/verification (Story 2.3-2.4)
- **bcrypt (>=4.1.0)**: Password hashing library (Story 2.2)
- **redis (>=5.0.0)**: Redis client for caching and sessions (Story 6+)

### uv Commands Reference

```bash
# Project management
uv init                    # Initialize new uv project (creates pyproject.toml)
uv add <package>          # Add dependency (main)
uv add --dev <package>    # Add dev dependency
uv sync                   # Install all dependencies (like poetry install)
uv lock                   # Generate lock file for reproducible installs
uv remove <package>       # Remove dependency

# Running code
uv run <command>          # Run command in venv context (like poetry run)
uv run uvicorn ...       # Run uvicorn through uv
uv run python script.py  # Run Python scripts in venv

# Inspection
uv pip list               # List installed packages
uv tree                   # Show dependency tree
```

### Testing Strategy

**Manual Verification:**
1. Directory structure check: `ls -la backend/src/`
2. Dependency verification: `uv pip list | grep -E "fastapi|uvicorn|sqlmodel"`
3. Server startup: `uv run uvicorn src.main:app --reload`
4. HTTP test: `curl http://localhost:8000` returns JSON response
5. Swagger UI: Browser access to `http://localhost:8000/docs` shows interactive API docs

**Future Testing (Stories 2+):**
- pytest integration tests for API endpoints
- Database connection testing with SQLModel
- Authentication flow testing with python-jose

### Technology Context

- **Language**: Python 3.10+ (per requires-python)
- **Framework**: FastAPI (modern, async-capable, auto-docs)
- **ASGI Server**: Uvicorn (ASGI implementation)
- **Async**: Python async/await support for high-performance I/O operations
- **Type Hints**: Pydantic v2 with Python type hints for validation

### Key Constraints

- Must use uv for dependency management (per project decision)
- Python version minimum 3.10 (required for type hints features)
- FastAPI requires Python 3.7+, but 3.10+ recommended for best experience
- `.venv` should be in backend folder (uv default behavior)

### Code Example - src/main.py

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Numerologist AI API",
    description="Backend API for Numerologist AI application",
    version="0.1.0"
)

# Configure CORS for mobile app (will be expanded in Story 1.6)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Will restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Numerologist AI API"}

@app.on_event("startup")
async def startup_event():
    print("Application startup")

@app.on_event("shutdown")
async def shutdown_event():
    print("Application shutdown")
```

---

## Learnings from Previous Story

**From Story 1.1 (Status: done)**

- **Foundation Structure Established**: Monorepo structure created with backend/ and mobile/ folders ready for population
- **Git Initialized**: All subsequent stories will build on committed work; git history established
- **Makefile & Docker Compose**: Development workflow automation already in place (make dev, make test, etc.)
- **Dependencies Pre-Configured**: Makefile can use `make dev` for running backend services

**Key Takeaway for This Story:**
- Continue using Makefile established in Story 1.1 for consistency; once backend uv setup is complete, may add additional backend-specific targets
- Git commits should follow established pattern: "Story X.Y: Description"

Source: [stories/1-1-initialize-monorepo-structure.md#Dev-Agent-Record]

---

## Dev Agent Record

### Context Reference

- **Story Context XML**: `/home/hieutt50/projects/numerologist-ai/docs/stories/1-2-setup-backend-with-uv-fastapi.context.xml`
- **Generated**: 2025-11-04
- **Status**: ready-for-dev

### Agent Model Used

Claude Haiku 4.5

### Completion Notes List

✅ **Story 1.2 COMPLETED** - All acceptance criteria satisfied

- [x] uv project successfully initialized in backend/
- [x] pyproject.toml configured with all required dependencies (FastAPI, Uvicorn, SQLModel, Alembic, etc.)
- [x] Python version constraint: >=3.10 set correctly (auto-upgraded to 3.11 by uv)
- [x] Dev dependencies added: pytest, black, ruff
- [x] Source folder structure created: src/, api/, core/, models/, services/
- [x] FastAPI app implemented with root endpoint returning correct JSON
- [x] CORS middleware configured for frontend integration
- [x] Startup/shutdown event handlers implemented
- [x] All dependencies installed successfully with uv sync (.venv created)
- [x] Server starts on localhost:8000 with hot reload
- [x] Root endpoint tested: `{"message": "Numerologist AI API"}` ✓
- [x] Health endpoint working: `{"status": "healthy"}` ✓
- [x] Swagger UI accessible at http://localhost:8000/docs ✓
- [x] All 7 tasks completed with all subtasks checked
- [x] All 9 acceptance criteria validated

**Implementation Notes:**
- Used uv 0.8.22 for fast, deterministic dependency management
- Backend structure follows common Python convention (src/ pattern)
- CORS configured permissively ("*") for development (will restrict in production)
- Event handlers use @app.on_event() decorator (established pattern)
- Added health check endpoint for monitoring
- git commit: d95adf7 - Story 1.2: Setup Backend with uv & FastAPI

### File List

**NEW FILES:**
- `backend/pyproject.toml` (1,127 bytes) - uv project configuration with dependencies
- `backend/.python-version` (22 bytes) - Python version specification (3.11)
- `backend/README.md` (1,037 bytes) - Project README generated by uv
- `backend/src/main.py` (1,758 bytes) - FastAPI app with root and health endpoints
- `backend/src/__init__.py` (0 bytes) - Python package marker
- `backend/uv.lock` (25,234 bytes) - uv lockfile with exact dependency versions
- `docs/stories/1-2-setup-backend-with-uv-fastapi.md` - This story file
- `docs/stories/1-2-setup-backend-with-uv-fastapi.context.xml` - Story context document

**DIRECTORIES CREATED:**
- `backend/` - Backend application root
- `backend/src/` - Source code root
- `backend/src/api/` - API routes directory (empty, populated in later stories)
- `backend/src/core/` - Core utilities directory (empty, populated in later stories)
- `backend/src/models/` - SQLModel ORM models directory (empty, populated in Story 1.5)
- `backend/src/services/` - Business logic services directory (empty, populated in later stories)
- `backend/.venv/` - Virtual environment created by uv sync

**GIT COMMITS:**
- d95adf7: Story 1.2: Setup Backend with uv & FastAPI

**KEY DEPENDENCIES INSTALLED:**
- fastapi 0.109.0+ - Web framework with auto OpenAPI docs
- uvicorn 0.38.0 - ASGI server with hot reload
- sqlmodel 0.0.27 - ORM (SQLAlchemy + Pydantic)
- alembic 1.17.1 - Database migrations
- pydantic 2.5.3 - Data validation
- python-jose 3.5.0 - JWT support
- bcrypt 5.0.0 - Password hashing
- redis 7.0.1 - Redis client

---

## References

- **Epic Breakdown**: [Source: docs/epics.md#Story-1.2-Setup-Backend-with-uv-FastAPI]
- **Previous Story Learnings**: [Source: docs/stories/1-1-initialize-monorepo-structure.md#Dev-Agent-Record]
- **Architecture**: [Source: docs/architecture.md#Backend-Architecture]
- **uv Documentation**: [External: https://docs.astral.sh/uv/]
- **FastAPI Documentation**: [External: https://fastapi.tiangolo.com/]

---

## Change Log

| Version | Date | Author | Notes |
|---------|------|--------|-------|
| 2.0 | 2025-11-04 | Claude (Dev Agent) | ✅ COMPLETED - All tasks done, all ACs satisfied, ready for code review |
| 1.1 | 2025-11-04 | Claude (SM Agent) | Story context XML generated, marked ready-for-dev |
| 1.0 | 2025-11-04 | Claude (SM Agent) | Initial draft from Epic 1, Story 1.2 |

