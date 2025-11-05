# Story 1.7: Makefile Development Workflow

**Epic:** Epic 1 - Foundation & Project Setup
**Story ID:** 1-7-makefile-development-workflow
**Status:** done
**Created:** 2025-11-05
**Updated:** 2025-11-05

---

## User Story

**As a** developer,
**I want** simple commands to start the entire development environment,
**So that** I can get coding quickly without remembering complex commands.

---

## Business Value

This story completes the foundation epic by providing a streamlined developer experience with simple, memorable commands. Instead of remembering complex Docker and server startup commands across multiple terminals, developers can use intuitive `make` commands to control the entire development environment. This reduces onboarding friction and increases development velocity.

---

## Acceptance Criteria

### AC1: Makefile Structure and Help System
- [ ] `Makefile` exists in root directory with proper .PHONY declarations
- [ ] `make help` (or just `make`) displays all available commands with descriptions
- [ ] Help output is well-formatted and easy to read
- [ ] Commands are grouped logically (dev, docker, database, utility)

### AC2: Docker Service Management
- [ ] `make docker-up` starts PostgreSQL and Redis containers in detached mode
- [ ] Command displays success message with service URLs (localhost:5432, localhost:6379)
- [ ] `make docker-down` stops all Docker services gracefully
- [ ] Commands provide clear feedback on what they're doing

### AC3: Backend Server Command
- [ ] `make backend` starts FastAPI server with auto-reload enabled
- [ ] Server starts on http://0.0.0.0:8000 (accessible from other devices)
- [ ] Command runs from backend directory using `uv run uvicorn`
- [ ] Clear output showing server is ready and where docs are available

### AC4: Mobile App Command
- [ ] `make mobile` starts Expo development server
- [ ] Command runs from mobile directory using `npm start`
- [ ] Expo Metro bundler starts successfully
- [ ] QR code displayed for mobile device connection

### AC5: Integrated Development Command
- [ ] `make dev` orchestrates full environment startup
- [ ] Executes `docker-up` first to ensure services are ready
- [ ] Starts backend and mobile in parallel (using `&` operator)
- [ ] Provides clear instructions on what URLs to visit

### AC6: Testing Command
- [ ] `make test` runs all backend tests via pytest
- [ ] Also runs all mobile tests (if test suite exists)
- [ ] Clear output showing test results for both environments
- [ ] Returns appropriate exit code (0 for pass, non-zero for fail)

### AC7: Cleanup Command
- [ ] `make clean` removes Python bytecode files (`__pycache__`, `*.pyc`)
- [ ] Cleans mobile cache (`node_modules/.cache`)
- [ ] Handles missing directories gracefully (no errors if already clean)
- [ ] Provides confirmation message when complete

### AC8: Database Migration Commands (Bonus)
- [ ] `make db-migrate MSG='description'` auto-generates migration from model changes
- [ ] `make db-upgrade` applies all pending migrations to database
- [ ] `make db-downgrade` rolls back the last applied migration
- [ ] `make db-current` shows current migration version
- [ ] `make db-history` displays full migration history
- [ ] All DB commands require MSG parameter where needed

### AC9: Error Handling
- [ ] Commands provide helpful error messages if prerequisites are missing
- [ ] Database migration commands validate required MSG parameter
- [ ] `make clean` doesn't fail if directories don't exist
- [ ] Commands use `@echo` for user-friendly output

### AC10: Documentation Updated
- [ ] README.md includes "Development Workflow" section
- [ ] Documents `make dev` as the primary quick-start command
- [ ] Lists all Makefile commands with brief descriptions
- [ ] Explains what each command does and when to use it

---

## Tasks

### Task 1: Verify Existing Makefile Structure
**Mapped to:** AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8
- [ ] Review existing Makefile in project root
- [ ] Verify all .PHONY declarations are present
- [ ] Check that all required commands exist (help, dev, backend, mobile, docker-up/down, test, clean)
- [ ] Verify bonus database migration commands exist
- [ ] Ensure proper target dependencies (e.g., `dev: docker-up`)

### Task 2: Test Docker Commands
**Mapped to:** AC2, AC9
- [ ] Run `make docker-up` and verify containers start
- [ ] Check PostgreSQL is accessible on localhost:5432
- [ ] Check Redis is accessible on localhost:6379
- [ ] Run `make docker-down` and verify containers stop cleanly
- [ ] Verify error messages are helpful if docker-compose.yml is missing

### Task 3: Test Backend Command
**Mapped to:** AC3, AC9
- [ ] Run `make backend` and verify FastAPI server starts
- [ ] Confirm server is accessible at http://localhost:8000
- [ ] Verify /docs endpoint loads successfully
- [ ] Confirm auto-reload works (touch a file, see reload)
- [ ] Test error message if backend dependencies not installed

### Task 4: Test Mobile Command
**Mapped to:** AC4, AC9
- [ ] Run `make mobile` and verify Expo server starts
- [ ] Confirm Metro bundler is running
- [ ] Verify QR code is displayed for device connection
- [ ] Test web preview works (press 'w' in terminal)
- [ ] Check error handling if node_modules missing

### Task 5: Test Integrated Dev Command
**Mapped to:** AC5
- [ ] Run `make dev` from clean state
- [ ] Verify Docker services start first
- [ ] Confirm backend and mobile both start in parallel
- [ ] Check that both services remain running simultaneously
- [ ] Verify clear instructions are displayed to user
- [ ] Test stopping services (Ctrl+C handling)

### Task 6: Test Testing and Cleanup Commands
**Mapped to:** AC6, AC7
- [ ] Run `make test` with backend tests present
- [ ] Verify pytest executes and shows results
- [ ] Run `make clean` and verify __pycache__ directories removed
- [ ] Confirm .pyc files deleted
- [ ] Verify mobile cache cleaned if present
- [ ] Test clean command runs without errors on already-clean project

### Task 7: Test Database Migration Commands
**Mapped to:** AC8, AC9
- [ ] Run `make db-current` to check current migration state
- [ ] Run `make db-history` to see migration history
- [ ] Test `make db-migrate` without MSG parameter (should error)
- [ ] Test `make db-migrate MSG="test migration"` (should create file)
- [ ] Test `make db-upgrade` to apply migrations
- [ ] Test `make db-downgrade` to rollback
- [ ] Verify all commands provide clear feedback

### Task 8: Update README Documentation
**Mapped to:** AC10
- [ ] Add "Development Workflow" section to README.md
- [ ] Document quick start: `make dev`
- [ ] List all Makefile commands in a table with descriptions
- [ ] Add examples of common workflows
- [ ] Document database migration workflow
- [ ] Include troubleshooting tips for common issues

### Task 9: End-to-End Validation
**Mapped to:** All ACs
- [ ] Start fresh in new terminal session
- [ ] Run `make help` to see all commands
- [ ] Run `make dev` and verify full environment starts
- [ ] Access backend API at http://localhost:8000/docs
- [ ] Access mobile app and see "API Status: Connected"
- [ ] Run `make test` to verify test suite
- [ ] Run `make clean` to cleanup
- [ ] Run `make docker-down` to stop services
- [ ] Document any issues or improvements needed

---

## Technical Implementation

### Makefile Structure

The Makefile follows GNU Make conventions with clear target organization:

```makefile
# Numerologist AI - Development Makefile
# This Makefile provides convenient commands for development workflow

.PHONY: help dev backend mobile docker-up docker-down test clean db-migrate db-upgrade db-downgrade db-current db-history db-revision

# Default target
help:
	@echo "Numerologist AI Development Commands"
	@echo ""
	@echo "  make help          - Show this help message"
	@echo "  make dev           - Start full development environment"
	@echo "  make backend       - Start backend API server only"
	@echo "  make mobile        - Start mobile app dev server only"
	@echo "  make docker-up     - Start PostgreSQL + Redis containers"
	@echo "  make docker-down   - Stop Docker containers"
	@echo "  make test          - Run all tests (backend + mobile)"
	@echo "  make clean         - Clean up generated files and caches"
	@echo ""
	@echo "Database Migration Commands:"
	@echo "  make db-migrate MSG='description'  - Auto-generate migration"
	@echo "  make db-upgrade                     - Apply all migrations"
	@echo "  make db-downgrade                   - Rollback last migration"
	@echo "  make db-current                     - Show current version"
	@echo "  make db-history                     - Show migration history"

# Start full development environment
dev: docker-up
	@echo "Starting Numerologist AI Development Environment..."
	@echo "🔧 Backend will start on http://localhost:8000"
	@echo "📱 Mobile app will start via Expo"
	@$(MAKE) backend & $(MAKE) mobile

# Individual service commands
backend:
	@echo "🔧 Starting Backend (FastAPI)..."
	cd backend && uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

mobile:
	@echo "📱 Starting Mobile App (Expo)..."
	cd mobile && npm start

docker-up:
	@echo "🐳 Starting Docker services..."
	docker-compose up -d
	@echo "✅ PostgreSQL: localhost:5432"
	@echo "✅ Redis: localhost:6379"

docker-down:
	@echo "🛑 Stopping Docker services..."
	docker-compose down

# Testing and cleanup
test:
	@echo "🧪 Running Backend Tests..."
	cd backend && uv run pytest
	@echo "🧪 Running Mobile Tests..."
	cd mobile && npm test

clean:
	@echo "🧹 Cleaning up..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	cd mobile && rm -rf node_modules/.cache 2>/dev/null || true
	@echo "✅ Cleaned up successfully"

# Database migration commands
db-migrate:
	@if [ -z "$(MSG)" ]; then echo "❌ Error: MSG required"; exit 1; fi
	cd backend && uv run alembic revision --autogenerate -m "$(MSG)"

db-upgrade:
	cd backend && uv run alembic upgrade head

db-downgrade:
	cd backend && uv run alembic downgrade -1

db-current:
	cd backend && uv run alembic current

db-history:
	cd backend && uv run alembic history

.DEFAULT_GOAL := help
```

### Key Design Decisions

**1. Phony Targets:**
All targets are declared as `.PHONY` because they don't produce files - they execute actions.

**2. Dependency Chain:**
`dev` depends on `docker-up` to ensure database services are ready before starting app servers.

**3. Parallel Execution:**
Backend and mobile start in parallel using `&` to maximize developer efficiency. Both services remain running until Ctrl+C.

**4. User Feedback:**
Every command uses `@echo` with emojis (🔧🐳🧪🧹) for clear, friendly feedback about what's happening.

**5. Error Suppression:**
`clean` command uses `2>/dev/null || true` to avoid errors when cleaning already-clean directories.

**6. Database Commands:**
Alembic migration commands wrapped in make targets for consistency with rest of workflow.

---

## Dev Notes

### Current State Analysis

**Makefile Already Exists:**
The Makefile was created during project setup and already includes all required commands from the acceptance criteria, PLUS bonus database migration commands. This story focuses on:
1. **Validation:** Testing each command works as expected
2. **Documentation:** Ensuring README.md documents the workflow
3. **Verification:** Confirming error handling is robust

**Existing Commands:**
- ✅ help, dev, backend, mobile (all core commands present)
- ✅ docker-up, docker-down (container management)
- ✅ test, clean (utility commands)
- ✅ **BONUS:** db-migrate, db-upgrade, db-downgrade, db-current, db-history (migration management)

### Learnings from Story 1.6 - Frontend API Service Setup

**From Story 1.6 Dev Agent Record:**

1. **Environment Variable Pattern**
   - Story 1.6 used `.env.example` to document configuration
   - Makefile should also be documented in README.md for discoverability
   - Pattern: Example file → Documentation → Clear instructions

2. **Service Integration Testing**
   - Story 1.6 validated end-to-end: backend running → mobile connects → status displayed
   - Makefile validation should follow same pattern: `make dev` → verify both services running → test connectivity

3. **Clear User Feedback**
   - Story 1.6 home screen showed clear status: "API Status: Connected"
   - Makefile commands use emojis and clear messages: "🔧 Starting Backend..."
   - Both prioritize developer experience with immediate feedback

4. **Files Created/Modified**
   - Story 1.6 created: `mobile/.env.example`
   - Story 1.6 modified: `mobile/src/services/api.ts`, `mobile/src/app/index.tsx`
   - Story 1.7 will modify: `README.md` (documentation)
   - Story 1.7 validates: `Makefile` (already exists)

5. **Testing Philosophy**
   - Test with services running AND stopped (error scenarios)
   - Story 1.7 should test: Docker services up/down, backend start/stop, error handling

### Integration with Previous Stories

**Story 1.4 - Docker Compose:**
- Created `docker-compose.yml` with PostgreSQL and Redis
- `make docker-up` wraps `docker-compose up -d` for convenience
- `make docker-down` ensures clean shutdown

**Story 1.5 - Database & Settings:**
- Added database migrations via Alembic
- Makefile extends this with `db-*` commands for migration workflow
- Centralizes database operations in one place

**Story 1.6 - Frontend API Service:**
- Established that full stack needs Docker → Backend → Mobile
- `make dev` codifies this startup sequence
- Provides the quick-start command mentioned in Story 1.6 prerequisite testing

### Prerequisites Verification

**Must exist before this story can be validated:**
- [x] Story 1.2: Backend with FastAPI (`backend/` folder, `uv` configured)
- [x] Story 1.3: Mobile with Expo (`mobile/` folder, `npm` configured)
- [x] Story 1.4: Docker Compose (`docker-compose.yml` with PostgreSQL + Redis)
- [x] Story 1.5: Database migrations (`alembic` configured)
- [x] Story 1.6: API client in mobile (`mobile/src/services/api.ts`)

All prerequisites are complete, making this story ready for validation.

### Testing Strategy

**Test Sequence:**
1. **Clean state**: Stop all services, clean up caches
2. **Test individual commands**: docker-up, backend, mobile (one at a time)
3. **Test integrated command**: `make dev` (all services together)
4. **Test utility commands**: test, clean, db-* (supporting workflow)
5. **Test error scenarios**: Missing dependencies, stopped services
6. **Document findings**: Update README with any discovered tips

**Expected Outcomes:**
- `make dev` successfully starts all three layers (Docker, backend, mobile)
- Developer can access http://localhost:8000/docs (backend API)
- Mobile app shows "API Status: Connected" (from Story 1.6)
- All commands provide clear feedback and handle errors gracefully

### README Documentation Plan

Add a new "Development Workflow" section to README.md with:

**Quick Start:**
```bash
# Start everything (Docker + Backend + Mobile)
make dev

# Visit http://localhost:8000/docs for API
# Press 'w' in Expo terminal for web preview
```

**Common Commands:**
| Command | Description |
|---------|-------------|
| `make help` | Show all available commands |
| `make dev` | Start full development environment |
| `make backend` | Start backend API server only |
| `make mobile` | Start mobile app only |
| `make docker-up` | Start PostgreSQL + Redis |
| `make test` | Run all tests |
| `make clean` | Clean up caches and bytecode |

**Database Migrations:**
```bash
# Create migration after changing models
make db-migrate MSG="add user email field"

# Apply migrations to database
make db-upgrade

# Check current version
make db-current
```

**Troubleshooting:**
- If backend fails: Check Docker services with `make docker-up`
- If mobile fails: Run `npm install` in mobile folder
- If tests fail: Check database is migrated with `make db-current`

### Architecture Alignment

**From architecture.md:**
- Development workflow section mentions starting backend and frontend separately
- Makefile codifies this into simple commands
- Testing section mentions pytest for backend - `make test` runs this
- Architecture recommends Docker Compose for local development - `make docker-up` provides this

**Project Structure:**
```
numerologist-ai/
├── Makefile              # ← This story validates this file
├── docker-compose.yml    # Used by `make docker-up`
├── backend/              # Used by `make backend`
│   ├── pyproject.toml    # uv dependency management
│   └── src/main.py       # FastAPI application
└── mobile/               # Used by `make mobile`
    ├── package.json      # npm dependency management
    └── src/app/index.tsx # Expo application
```

### References

- [Source: docs/epics.md#Epic-1-Story-1.7] - Original story requirements
- [Source: docs/architecture.md#Development-Workflow] - Workflow context
- [Source: docs/stories/1-6-frontend-api-service-setup.md] - Previous story learnings
- [Source: Makefile] - Existing implementation to validate

---

## Dev Agent Record

### Context Reference

- docs/stories/1-7-makefile-development-workflow.context.xml

### Agent Model Used

{{agent_model_name_version}}

### Debug Log

<!-- Implementation notes will be added here during development -->

### Completion Notes List

<!-- Will be populated during implementation with:
- Validation results for each command
- Any issues found and fixed
- Documentation updates made
- End-to-end test results
-->

### File List

<!-- Will be populated with files modified during implementation:
- VALIDATED: Makefile (existing file, all commands tested)
- MODIFIED: README.md (documentation added)
-->

---

## Definition of Done

- [ ] All acceptance criteria verified
- [ ] All tasks completed
- [ ] `make help` displays all commands
- [ ] `make docker-up` starts PostgreSQL and Redis
- [ ] `make backend` starts FastAPI server successfully
- [ ] `make mobile` starts Expo dev server successfully
- [ ] `make dev` starts full environment (Docker → Backend → Mobile)
- [ ] `make test` runs all tests (backend + mobile)
- [ ] `make clean` cleans up caches without errors
- [ ] Database migration commands work (db-migrate, db-upgrade, etc.)
- [ ] Error handling tested (missing dependencies, stopped services)
- [ ] README.md updated with Development Workflow section
- [ ] End-to-end validation: `make dev` → API accessible → Mobile shows "Connected"
- [ ] Git commit created with message: "Story 1.7: Makefile Development Workflow - Validation Complete"

---

## Testing Checklist

### Test Scenario 1: Individual Command Validation
- [ ] Run `make help` - verify all commands listed
- [ ] Run `make docker-up` - verify PostgreSQL and Redis start
- [ ] Run `make backend` - verify FastAPI starts on :8000
- [ ] Run `make mobile` - verify Expo starts with QR code
- [ ] Run `make docker-down` - verify services stop

### Test Scenario 2: Integrated Development Command
- [ ] Stop all services
- [ ] Run `make dev` from clean state
- [ ] Verify Docker services start first
- [ ] Verify backend and mobile start in parallel
- [ ] Access http://localhost:8000/docs - verify API docs load
- [ ] Open mobile app - verify "API Status: Connected" displays
- [ ] Ctrl+C - verify both services stop gracefully

### Test Scenario 3: Database Migration Commands
- [ ] Run `make db-current` - verify shows current migration
- [ ] Run `make db-history` - verify shows migration list
- [ ] Run `make db-migrate` without MSG - verify error message
- [ ] Run `make db-migrate MSG="test"` - verify creates migration
- [ ] Run `make db-upgrade` - verify applies migration
- [ ] Run `make db-downgrade` - verify rolls back

### Test Scenario 4: Testing and Cleanup
- [ ] Run `make test` - verify backend tests execute
- [ ] Create __pycache__ and .pyc files manually
- [ ] Run `make clean` - verify files removed
- [ ] Run `make clean` again - verify no errors (idempotent)
- [ ] Check mobile node_modules/.cache cleaned if present

### Test Scenario 5: Error Handling
- [ ] Run `make backend` without Docker - verify helpful error
- [ ] Run `make mobile` without node_modules - verify error message
- [ ] Run `make db-upgrade` without database - verify clear error
- [ ] Test all commands provide user-friendly feedback

---

## Change Log

| Version | Date       | Author | Changes |
|---------|------------|--------|---------|
| 1.0     | 2025-11-05 | SM     | Initial story draft - validation focus since Makefile exists |

---

**Ready for Development:** Yes (Validation and documentation tasks)
**Blocked By:** None (All prerequisites complete)
**Blocking:** Epic 1 completion, Epic 2 stories
