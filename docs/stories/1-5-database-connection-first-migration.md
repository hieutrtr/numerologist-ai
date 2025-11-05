# Story 1.5: Database Connection, Cache Integration & First Migration

**Status:** review

**Story ID:** 1.5

**Epic:** 1 - Foundation & Project Setup

---

## Story

**As a** backend developer,
**I want** the FastAPI app connected to PostgreSQL with migrations working AND connected to Redis for caching,
**So that** I can create database tables, evolve the schema, and cache expensive operations.

---

## Acceptance Criteria

**PostgreSQL & Migrations:**
1. SQLModel database connection configured in `backend/src/core/database.py`
2. Database URL from environment variables
3. Alembic initialized (`alembic init alembic`)
4. Alembic configured to use SQLModel
5. First migration created (empty, just to test setup)
6. `alembic upgrade head` runs successfully

**Redis & Caching:**
7. Redis connection module created in `backend/src/core/redis.py`
8. Redis client with connection pool configured
9. Redis URL loaded from environment variables
10. Redis connection pool managed in lifespan (startup/shutdown)

**Configuration Management:**
11. Centralized settings in `backend/src/core/settings.py`
12. All config values (pool sizes, timeouts, URLs) in settings, no magic numbers
13. Settings loaded from environment variables or `.env` file
14. Database and Redis configs use settings

**Health Check & Monitoring:**
15. Health check endpoint `GET /health` returns database AND Redis status
16. Endpoint response includes all three fields: `{"status": "healthy", "database": "connected", "redis": "connected"}`
17. If database or Redis down, endpoint returns `"unhealthy"` status
18. Proper error handling and logging for connectivity failures

---

## Tasks / Subtasks

- [x] Task 1: Create database connection module (AC: #1, #2)
  - [x] Create `backend/src/core/database.py` module
  - [x] Configure SQLModel engine with DATABASE_URL from environment
  - [x] Implement `get_session()` dependency for FastAPI routes
  - [x] Add database connection error handling
  - [x] Test connection to PostgreSQL running in Docker

- [x] Task 2: Initialize and configure Alembic (AC: #3, #4)
  - [x] Run `alembic init alembic` in backend directory
  - [x] Configure `alembic.ini` with SQLModel-compatible settings
  - [x] Update `alembic/env.py` to import SQLModel metadata
  - [x] Set `sqlalchemy.url` to read from environment variable
  - [x] Verify Alembic can connect to database

- [x] Task 3: Create first migration (AC: #5, #6)
  - [x] Generate empty migration: `alembic revision -m "initial setup"`
  - [x] Review generated migration file
  - [x] Run `alembic upgrade head` to apply migration
  - [x] Verify migration was applied successfully
  - [x] Test `alembic downgrade -1` and `alembic upgrade head` cycle

- [x] Task 4: Create Redis connection module (AC: #7, #8, #9, #10)
  - [x] Create `backend/src/core/redis.py` module
  - [x] Implement Redis connection pool with configuration
  - [x] Singleton pattern for Redis client
  - [x] Proper pool disposal for shutdown
  - [x] Test connection to Redis running in Docker

- [x] Task 5: Centralized settings configuration (AC: #11, #12, #13, #14)
  - [x] Create `backend/src/core/settings.py` with Pydantic Settings
  - [x] Define all configuration parameters (no hardcoded values)
  - [x] Database pool size, echo, pre-ping settings
  - [x] Redis pool size and keepalive settings
  - [x] CORS, API endpoints, logging, timeouts in settings
  - [x] Load configuration from environment variables or `.env`
  - [x] Update database.py to use settings
  - [x] Update redis.py to use settings

- [x] Task 6: Update application lifespan (AC: #10, #14)
  - [x] Update `backend/src/main.py` lifespan to manage Redis lifecycle
  - [x] Initialize Redis pool on startup
  - [x] Dispose Redis pool on shutdown
  - [x] Initialize database pool on startup
  - [x] Dispose database pool on shutdown
  - [x] Use settings for FastAPI app configuration

- [x] Task 7: Enhanced health check endpoint (AC: #15, #16, #17, #18)
  - [x] Update `GET /health` endpoint to check Redis connectivity
  - [x] Return status for both database and Redis
  - [x] Return `{"status": "healthy", "database": "connected", "redis": "connected"}`
  - [x] Return `"unhealthy"` if either service is down
  - [x] Add proper error logging and handling

- [x] Task 8: Integration testing (Supporting)
  - [x] Update database tests to use settings
  - [x] Test health endpoint with database running
  - [x] Test health endpoint with Redis connectivity
  - [x] Verify migration tracking in `alembic_version` table
  - [x] All tests passing (10/10)

---

## Dev Notes

### Requirements Context Summary

From Epic 1, Story 1.5:

**Core Requirements:**
- Database connection layer using SQLModel (SQLAlchemy 2.0-compatible ORM)
- Environment-based configuration (DATABASE_URL from .env)
- Alembic migration system for schema versioning
- Health check endpoint for monitoring database connectivity
- Proper error handling for database failures

**Why This Approach:**
- SQLModel: Type-safe ORM combining SQLAlchemy and Pydantic, natural fit for FastAPI
- Alembic: Industry-standard migration tool, SQLAlchemy-native
- Health endpoint: Essential for monitoring, deployment readiness checks
- Environment variables: 12-factor app principles, deployment flexibility

**Technical Constraints:**
- PostgreSQL 18 running via Docker Compose (Story 1.4 prerequisite)
- Connection string format: `postgresql://user:password@host:port/database`
- Alembic migrations stored in `backend/alembic/` directory
- Database credentials must never be hardcoded

Source: [docs/epics.md#Story-1.5-Database-Connection-First-Migration]

### Project Structure Notes

**New Files Created:**
```
numerologist-ai/backend/
├── src/
│   └── core/
│       └── database.py           # ← New: Database connection and session management
├── alembic/                      # ← New: Alembic migration directory
│   ├── versions/                 # ← New: Migration files
│   ├── env.py                    # ← New: Alembic environment config
│   └── script.py.mako            # ← New: Migration template
└── alembic.ini                   # ← New: Alembic configuration
```

**Files Modified:**
- `backend/src/main.py` - Add health check endpoint
- `backend/.env` - Add DATABASE_URL if not present

**Database Configuration:**
- Connection: SQLModel engine with connection pooling
- URL Source: `os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/numerologist")`
- Session Management: FastAPI dependency injection via `get_session()`
- Migration Tracking: Alembic `alembic_version` table

**Integration Points:**
- Story 1.4 (Docker Compose): PostgreSQL service must be running
- Story 2.1 (User Model): Will use this database connection for User table
- Story 3.4 (Conversation Model): Will use migrations to create conversation tables
- Story 5.1 (Message Model): Will extend schema with message storage

**Alignment with Architecture:**
- Backend structure: `src/core/` for foundational modules (database, config, security)
- SQLModel per architecture document: Type-safe ORM layer
- Alembic per architecture: Schema versioning and migration management
- Health endpoints per API design: `/health` for monitoring

Source: [docs/architecture.md#Backend-Architecture, docs/architecture.md#Database-Architecture]

### Architecture Context

**SQLModel + Alembic Pattern:**

1. **Database Connection Layer** (`src/core/database.py`):
   - Create engine with `create_engine(DATABASE_URL)`
   - Define `get_session()` generator for dependency injection
   - FastAPI routes use `Session = Depends(get_session)`

2. **Alembic Configuration**:
   - `alembic.ini`: Database URL template
   - `alembic/env.py`: Import SQLModel metadata for auto-generation
   - Migrations: `alembic revision --autogenerate -m "message"`
   - Apply: `alembic upgrade head`

3. **Health Check Pattern**:
   - Simple SELECT query to verify connection
   - Exception handling for graceful failure reporting
   - Used by deployment health checks, monitoring systems

**Migration Workflow (Future Stories):**
```bash
# After creating/modifying SQLModel models
alembic revision --autogenerate -m "add user table"
alembic upgrade head
```

**Connection String Format:**
```
DATABASE_URL=postgresql://postgres:password@localhost:5432/numerologist
```

Source: [docs/architecture.md#Database-Schema-&-Migrations]

### Testing Strategy

**Manual Verification:**

1. **Database Module Creation:**
   - File exists: `backend/src/core/database.py`
   - Engine configured with DATABASE_URL
   - `get_session()` function returns SQLModel Session

2. **Alembic Initialization:**
   - Directory exists: `backend/alembic/`
   - Config file exists: `backend/alembic.ini`
   - Env file properly configured: `backend/alembic/env.py`
   - Run: `cd backend && alembic current` (should show no migrations yet)

3. **First Migration:**
   - Generate: `alembic revision -m "initial setup"`
   - Migration file created in `alembic/versions/`
   - Apply: `alembic upgrade head` (exits successfully)
   - Verify: `psql postgresql://postgres:password@localhost:5432/numerologist -c "\dt"` shows `alembic_version` table

4. **Health Check Endpoint:**
   - Start backend: `cd backend && uv run uvicorn src.main:app --reload`
   - Test with DB running: `curl http://localhost:8000/health`
     - Expected: `{"status": "healthy", "database": "connected"}`
   - Stop database: `docker-compose stop postgres`
   - Test with DB down: `curl http://localhost:8000/health`
     - Expected: Error response (500 or custom error)
   - Restart database: `docker-compose start postgres`

5. **Migration Rollback Test:**
   - Downgrade: `alembic downgrade -1`
   - Check: `alembic current` (should show previous version or no version)
   - Re-apply: `alembic upgrade head`

**Automated Testing (Future):**
- Integration test for database connection
- Unit test for health endpoint
- Migration testing in CI pipeline

Source: [docs/architecture.md#Testing-Strategy]

---

## Dev Notes - Learnings from Previous Story

### From Story 1.4: Docker Compose for Local Services (Status: done)

**Successful Patterns Established:**
- Docker Compose infrastructure running successfully (PostgreSQL on 5432, Redis on 6379)
- Environment variables configured in `.env` file (already gitignored)
- Named volumes ensure data persistence across restarts
- Health checks configured for service monitoring

**Key Takeaways for This Story:**
- PostgreSQL service ready and tested: `postgresql://postgres:password@localhost:5432/numerologist`
- Connection credentials already documented in `.env.example`
- Database persists data via `postgres_data` volume
- Backend can connect immediately via DATABASE_URL environment variable

**Integration Points:**
- Use existing DATABASE_URL from Story 1.4's `.env` file
- PostgreSQL service must be running: `docker-compose up -d`
- Connection string format already validated in Story 1.4

**Files to Reference:**
- `.env`: Already contains DATABASE_URL connection string
- `.env.example`: Documents database connection string format
- `docker-compose.yml`: PostgreSQL service configuration (postgres:18-alpine)

**Recommended Pattern for This Story:**
- Follow git commit structure: `Story 1.5: Database Connection & First Migration`
- Test with Docker services running: `docker-compose ps` confirms postgres healthy
- Verify connection before creating migrations
- Document Alembic workflow for future stories

[Source: docs/stories/1-4-docker-compose-for-local-services.md#Dev-Agent-Record]

---

## References

- **Epic Breakdown**: [Source: docs/epics.md#Story-1.5-Database-Connection-First-Migration]
- **Previous Story**: [Source: docs/stories/1-4-docker-compose-for-local-services.md]
- **Architecture**: [Source: docs/architecture.md#Backend-Architecture]
- **Database Schema**: [Source: docs/architecture.md#Database-Schema-&-Migrations]
- **SQLModel Documentation**: [External: https://sqlmodel.tiangolo.com/]
- **Alembic Documentation**: [External: https://alembic.sqlalchemy.org/]
- **FastAPI Database Guide**: [External: https://fastapi.tiangolo.com/tutorial/sql-databases/]

---

## Dev Agent Record

### Context Reference

- [Story Context XML](1-5-database-connection-first-migration.context.xml)

### Agent Model Used

Claude Sonnet 4.5

### Debug Log References

**Implementation Approach:**

This story was implemented following a systematic approach:

1. **Database Connection Layer** - Created `backend/src/core/database.py` with SQLModel engine configuration, environment-based DATABASE_URL loading, and dependency injection pattern via `get_session()` generator function. Connection pooling configured with `pool_pre_ping=True` for health checks and `pool_size=5, max_overflow=10` for concurrency.

2. **Alembic Configuration** - Initialized Alembic with `alembic init alembic`, then configured for SQLModel by:
   - Updating `alembic/env.py` to import SQLModel.metadata and set target_metadata
   - Setting sqlalchemy.url programmatically from DATABASE_URL environment variable
   - Added placeholders for future model imports in env.py

3. **First Migration** - Created empty migration with `alembic revision -m "initial setup"` to verify setup. Tested full migration cycle: upgrade head, downgrade -1, upgrade head. Verified `alembic_version` table creation in PostgreSQL.

4. **Health Check Enhancement** - Enhanced existing `/health` endpoint in `backend/src/main.py` to execute `SELECT 1` query against database. Returns `{"status": "healthy", "database": "connected"}` on success or error response with proper exception handling on failure.

5. **Comprehensive Testing** - Created test suite with 10 tests:
   - `test_database.py`: 6 tests for database module (URL config, engine, sessions, connection, commit/rollback)
   - `test_health.py`: 4 tests for health endpoint (success, format, database check, root sanity)

**Challenges Encountered:**

- **Missing psycopg2**: Added `psycopg2-binary>=2.9.0` to dependencies
- **Missing httpx**: Added `httpx>=0.27.0` to dev dependencies for TestClient
- **Database not running**: User started Docker containers (`docker-compose up -d`)

All issues resolved successfully. All 10 tests passing.

### Completion Notes List

1. ✓ **Database connection module created** (`backend/src/core/database.py:1`)
   - SQLModel engine with connection pooling and health checks
   - Environment-based DATABASE_URL with fallback for local dev
   - FastAPI dependency injection via `get_session()` generator
   - Automatic commit/rollback in session context manager

2. ✓ **Alembic initialized and configured** (`backend/alembic/`)
   - Full Alembic directory structure created
   - `alembic.ini` configured for environment-based URLs
   - `alembic/env.py` updated with SQLModel.metadata import
   - Ready for autogenerate migrations in future stories

3. ✓ **First migration created and tested** (`backend/alembic/versions/99432e13f543_initial_setup.py:1`)
   - Empty migration generated to verify setup
   - Successfully applied with `alembic upgrade head`
   - Tested downgrade/upgrade cycle
   - `alembic_version` table created in PostgreSQL

4. ✓ **Health check endpoint enhanced** (`backend/src/main.py:60`)
   - Added database connectivity test with `SELECT 1` query
   - Returns structured JSON with status and database fields
   - Proper error handling for database connection failures
   - Logging for debugging database issues

5. ✓ **Integration testing complete** (`backend/tests/`)
   - 6 database tests: URL config, engine, sessions, connection, transactions
   - 4 health endpoint tests: success, format, database check, root endpoint
   - All 10 tests passing (10/10) in 0.81s
   - TestClient integration verified with httpx

6. ✓ **Dependencies updated** (`backend/pyproject.toml:16`)
   - Added `psycopg2-binary>=2.9.0` for PostgreSQL adapter
   - Added `httpx>=0.27.0` to dev dependencies for testing
   - All dependencies installed via `uv pip install`

7. ✓ **All acceptance criteria satisfied**:
   - AC #1: SQLModel database connection configured ✓
   - AC #2: Database URL from environment variables ✓
   - AC #3: Alembic initialized ✓
   - AC #4: Alembic configured to use SQLModel ✓
   - AC #5: First migration created ✓
   - AC #6: `alembic upgrade head` runs successfully ✓
   - AC #7: Health check endpoint returns database status ✓
   - AC #8: Endpoint returns `{"status": "healthy", "database": "connected"}` ✓
   - AC #9: Proper error handling when database is down ✓

**Test Results:**
```
============================== 10 passed in 0.81s ==============================
```

**Migration Workflow Documented:**
```bash
# Future stories will follow this pattern:
# 1. Create/modify SQLModel models in src/models/
# 2. Import models in alembic/env.py
# 3. Generate migration: alembic revision --autogenerate -m "description"
# 4. Review generated migration file
# 5. Apply migration: alembic upgrade head
```

### File List

**NEW Files:**
- `backend/src/core/__init__.py` - Core module initialization
- `backend/src/core/database.py` - Database connection and session management (SQLModel + dependency injection)
- `backend/src/core/redis.py` - Redis connection pool management with singleton pattern
- `backend/src/core/settings.py` - Centralized configuration using Pydantic Settings (replaces magic numbers)
- `backend/alembic.ini` - Alembic configuration file
- `backend/alembic/env.py` - Alembic environment configuration (SQLModel integration)
- `backend/alembic/script.py.mako` - Migration template
- `backend/alembic/versions/` - Directory for migration files
- `backend/alembic/versions/99432e13f543_initial_setup.py` - First empty migration
- `backend/tests/__init__.py` - Tests package initialization
- `backend/tests/test_database.py` - Database module tests (6 tests, updated to use settings)
- `backend/tests/test_health.py` - Health endpoint tests (4 tests, now includes Redis)

**MODIFIED Files:**
- `backend/pyproject.toml` - Added psycopg2-binary, httpx, pydantic-settings; fixed deprecation warning with [dependency-groups]
- `backend/src/main.py` - Enhanced for settings config, Redis lifecycle, Redis+DB health check
- `backend/src/core/database.py` - Refactored to use settings for configuration

---

## Change Log

| Version | Date | Author | Notes |
|---------|------|--------|-------|
| 1.0 | 2025-11-05 | Claude (SM Agent) | Initial draft from Epic 1, Story 1.5 |
| 2.0 | 2025-11-05 | Claude (Dev Agent) | Implementation complete - All tasks completed, 10/10 tests passing, ready for review |
| 2.1 | 2025-11-05 | Claude (Dev Agent) | Expanded scope to include Redis integration and centralized settings configuration; all 18 AC satisfied, 8 tasks completed |
