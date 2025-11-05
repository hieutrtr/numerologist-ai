# Story 2.1: User Model & Database Schema

**Epic:** Epic 2 - User Authentication & Profile
**Story ID:** 2-1-user-model-database-schema
**Status:** ready-for-dev
**Created:** 2025-11-05
**Updated:** 2025-11-05

---

## User Story

**As a** backend developer,
**I want** a User database model with all required fields,
**So that** I can store user information securely.

---

## Business Value

This story establishes the foundation for user authentication by creating the User database model and schema. It enables all subsequent auth stories (registration, login, profile) by providing the data layer for storing user information. Secure storage of user data (especially password hashing) is critical for user trust and regulatory compliance (GDPR).

---

## Acceptance Criteria

### AC1: User Model Created with SQLModel
- [ ] File `backend/src/models/user.py` exists
- [ ] `User` class defined inheriting from `SQLModel` with `table=True`
- [ ] Model uses proper SQLModel field declarations
- [ ] All type hints are correct and use Python 3.11+ syntax

### AC2: Required Fields Defined
- [ ] `id: UUID` with `default_factory=uuid4` and `primary_key=True`
- [ ] `email: str` with `unique=True` and `index=True`
- [ ] `hashed_password: str | None = None` (nullable for OAuth users, no unique constraint)
- [ ] `full_name: str` (user's display name)
- [ ] `birth_date: date` (required for numerology calculations)
- [ ] `created_at: datetime` with `default_factory=datetime.utcnow`
- [ ] `updated_at: datetime` with `default_factory=datetime.utcnow`
- [ ] `is_active: bool` with `default=True`

### AC3: Database Constraints and Indexes
- [ ] Email field has `UNIQUE` constraint
- [ ] Email field has database index for fast lookups
- [ ] Primary key on `id` field
- [ ] No password field accepts plain text (only hashed_password)
- [ ] hashed_password is nullable (NULL for OAuth users without passwords)

### AC4: Model Imports and Dependencies
- [ ] SQLModel imported from sqlmodel
- [ ] UUID and uuid4 imported from uuid
- [ ] date and datetime imported from datetime
- [ ] Field imported from sqlmodel for field configuration
- [ ] All imports follow project conventions

### AC5: Model Registered with Alembic
- [ ] User model imported in `backend/src/models/__init__.py`
- [ ] Model discoverable by Alembic auto-generation
- [ ] No circular import issues

### AC6: Alembic Migration Generated
- [ ] Alembic migration created using `alembic revision --autogenerate -m "create users table"`
- [ ] Migration file exists in `backend/alembic/versions/`
- [ ] Migration file contains `create_table('user')` operation
- [ ] All fields present in migration
- [ ] Unique constraint on email in migration
- [ ] Index on email in migration

### AC7: Migration Applied Successfully
- [ ] `alembic upgrade head` executes without errors
- [ ] Database connection successful during migration
- [ ] Migration shows as current version in `alembic_version` table
- [ ] `alembic current` shows the new migration

### AC8: Database Table Verification
- [ ] Can connect to PostgreSQL: `psql $DATABASE_URL`
- [ ] `\dt` command shows `user` table
- [ ] `\d user` shows correct columns and types
- [ ] Email column has unique index
- [ ] Primary key constraint on id column

### AC9: Model Validation and Constraints
- [ ] Pydantic validation works (SQLModel uses Pydantic)
- [ ] Email validation ensures proper email format
- [ ] Birth date validation prevents future dates
- [ ] Created_at and updated_at automatically set on creation
- [ ] is_active defaults to True

### AC10: Integration with Core Database Module
- [ ] User model can be queried using get_session() dependency
- [ ] Can create user: `session.add(user); session.commit()`
- [ ] Can query user: `session.exec(select(User).where(User.email == email)).first()`
- [ ] Database session management works correctly

---

## Tasks

### Task 1: Create User Model File
**Mapped to:** AC1, AC2, AC4
- [ ] Create `backend/src/models/user.py` file
- [ ] Import required dependencies (SQLModel, Field, UUID, datetime)
- [ ] Define User class with SQLModel and table=True
- [ ] Add all 8 required fields with proper types
- [ ] Set field constraints (unique, index, primary_key, defaults)
- [ ] Add docstring describing the User model

### Task 2: Register Model with Alembic
**Mapped to:** AC5
- [ ] Edit `backend/src/models/__init__.py`
- [ ] Import User model: `from src.models.user import User`
- [ ] Export User in `__all__` list if present
- [ ] Verify no circular import issues
- [ ] Test import: `python -c "from src.models import User; print(User)"`

### Task 3: Generate Alembic Migration
**Mapped to:** AC6
- [ ] Ensure database is running: `docker ps` shows PostgreSQL
- [ ] Run: `cd backend && alembic revision --autogenerate -m "create users table"`
- [ ] Verify migration file created in `backend/alembic/versions/`
- [ ] Review migration file for correctness:
  - [ ] `op.create_table('user', ...)` present
  - [ ] All 8 columns defined with correct types
  - [ ] Unique constraint on email
  - [ ] Index on email
  - [ ] Primary key on id

### Task 4: Apply Migration to Database
**Mapped to:** AC7
- [ ] Run: `cd backend && alembic upgrade head`
- [ ] Verify output shows "Running upgrade -> [hash], create users table"
- [ ] No errors in migration output
- [ ] Run: `alembic current` to verify migration applied
- [ ] Check alembic_version table has new version

### Task 5: Verify Database Table Creation
**Mapped to:** AC8
- [ ] Connect to database: `psql $DATABASE_URL`
- [ ] Run `\dt` to list tables - verify `user` table exists
- [ ] Run `\d user` to describe table structure
- [ ] Verify all 8 columns present with correct types:
  - [ ] id: uuid (primary key)
  - [ ] email: character varying (unique, indexed)
  - [ ] hashed_password: character varying
  - [ ] full_name: character varying
  - [ ] birth_date: date
  - [ ] created_at: timestamp without time zone
  - [ ] updated_at: timestamp without time zone
  - [ ] is_active: boolean
- [ ] Verify constraints: `\d user` shows unique constraint on email
- [ ] Verify indexes: `\di` shows index on user.email

### Task 6: Test Model CRUD Operations
**Mapped to:** AC10
- [ ] Create test script or use Python shell
- [ ] Test user creation:
  ```python
  from src.models.user import User
  from src.core.database import get_session
  from datetime import date

  user = User(
      email="test@example.com",
      hashed_password="hashed_value_here",
      full_name="Test User",
      birth_date=date(1990, 1, 1)
  )
  # Verify created_at, updated_at, is_active auto-set
  # Verify id auto-generated
  ```
- [ ] Test database insertion (manual session test)
- [ ] Test email uniqueness constraint (try inserting duplicate)
- [ ] Test query by email
- [ ] Test query by id
- [ ] Test update operation
- [ ] Verify all operations work correctly

### Task 7: Validation Testing
**Mapped to:** AC9
- [ ] Test invalid email format (should fail Pydantic validation)
- [ ] Test missing required fields (email, full_name, birth_date)
- [ ] Test future birth_date (should be validated in API layer later)
- [ ] Test default values (created_at, updated_at, is_active)
- [ ] Test UUID auto-generation
- [ ] Document any validation that needs API-layer implementation

### Task 8: Documentation and Code Comments
**Mapped to:** All ACs
- [ ] Add docstring to User model explaining its purpose
- [ ] Add inline comments for non-obvious field configurations
- [ ] Update architecture.md if needed (data models section)
- [ ] Document any deviations from architecture.md
- [ ] Add migration notes if manual steps were required

### Task 9: Rollback Testing
**Mapped to:** AC6, AC7
- [ ] Test migration rollback: `alembic downgrade -1`
- [ ] Verify user table is dropped
- [ ] Test migration reapply: `alembic upgrade head`
- [ ] Verify user table is recreated
- [ ] Ensure migration is reversible

---

## Technical Implementation

### User Model Structure

**File: backend/src/models/user.py**

```python
"""
User Model

Defines the User database model for authentication and profile management.
This model stores core user information including authentication credentials
(hashed passwords) and personal information required for numerology calculations.
"""

from sqlmodel import SQLModel, Field
from datetime import date, datetime
from uuid import UUID, uuid4
from typing import Optional


class User(SQLModel, table=True):
    """
    User model for authentication and profile management.

    Stores user credentials, personal information, and account status.
    Passwords are NEVER stored in plain text - only bcrypt hashed values.
    Birth date is required for numerology calculations (Life Path, etc.).

    Relationships:
    - numerology_profile: One-to-one with NumerologyProfile (future story)
    - conversations: One-to-many with Conversation (future story)
    """

    # Primary key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique identifier for the user"
    )

    # Authentication fields
    email: str = Field(
        unique=True,
        index=True,
        description="User's email address (unique, used for login)"
    )
    hashed_password: str | None = Field(
        default=None,
        description="Bcrypt hashed password (NEVER store plain text). NULL for OAuth users."
    )

    # Profile fields
    full_name: str = Field(
        description="User's full name for display"
    )
    birth_date: date = Field(
        description="User's birth date (required for numerology calculations)"
    )

    # Metadata fields
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when user account was created"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when user account was last updated"
    )
    is_active: bool = Field(
        default=True,
        description="Whether the user account is active (False = soft delete)"
    )
```

### Model Registration

**File: backend/src/models/__init__.py**

```python
"""
Models Package

Imports all database models for SQLModel/Alembic auto-discovery.
This file must import all models to ensure Alembic can detect them
for automatic migration generation.
"""

from src.models.user import User

# Export all models
__all__ = ["User"]
```

### Alembic Migration

**Command to generate migration:**
```bash
cd backend
alembic revision --autogenerate -m "create users table"
```

**Expected migration file structure:**
```python
"""create users table

Revision ID: [auto-generated]
Revises: [previous-revision]
Create Date: [auto-generated]
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '[auto-generated]'
down_revision = '[previous-revision]'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'user',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=False),
        sa.Column('birth_date', sa.Date(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    # Create index on email for fast lookups
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)


def downgrade() -> None:
    # Drop index
    op.drop_index(op.f('ix_user_email'), table_name='user')
    # Drop table
    op.drop_table('user')
```

### Database Verification Commands

```bash
# Apply migration
cd backend
alembic upgrade head

# Verify migration applied
alembic current

# Should show:
# [revision_id] (head) create users table

# Connect to PostgreSQL
docker exec -it numerologist-postgres psql -U postgres -d numerologist

# Inside psql:
\dt              # List tables - should show 'user'
\d user          # Describe user table structure
\di              # List indexes - should show ix_user_email
SELECT * FROM alembic_version;  # Verify migration version

# Test data insertion (optional)
INSERT INTO "user" (id, email, hashed_password, full_name, birth_date, created_at, updated_at, is_active)
VALUES (
    gen_random_uuid(),
    'test@example.com',
    'fake_hash_for_testing',
    'Test User',
    '1990-01-01',
    NOW(),
    NOW(),
    TRUE
);

# Verify insertion
SELECT id, email, full_name, birth_date, is_active FROM "user";
```

---

## Dev Notes

### Integration with Previous Stories

**Story 1.5 - Database Connection & First Migration:**
- Story 1.5 established the database connection using settings.DATABASE_URL
- Story 1.5 created the first Alembic migration (initial setup)
- This story builds on that by adding the first real table migration
- Uses the same `get_session()` dependency established in Story 1.5

**Story 1.7 - Makefile Development Workflow:**
- Can use `make db-migrate MSG="create users table"` for migration generation
- Can use `make db-upgrade` to apply migrations
- Can use `make db-current` to verify migration applied
- Can use `make db-history` to see migration history
- Makefile commands make database operations consistent and easy

### Learnings from Story 1.7

**From Story 1.7 Dev Agent Record:**

1. **Documentation Pattern**
   - Story 1.7 emphasized comprehensive documentation in README.md
   - This story should update architecture.md with User model details
   - Pattern: Code → Documentation → Verification

2. **Testing Philosophy**
   - Test with services running (Docker PostgreSQL up)
   - Test migration forward AND backward (reversibility)
   - Test constraints (unique email) actually work
   - Verify via multiple methods (alembic current + psql \dt)

3. **Clear User Feedback**
   - Alembic provides migration feedback (Running upgrade...)
   - Use `make db-current` for quick status check
   - Document expected output for each command

4. **Files Created/Modified**
   - Story 2.1 will create: `backend/src/models/user.py`
   - Story 2.1 will modify: `backend/src/models/__init__.py`
   - Story 2.1 will create: New Alembic migration file
   - Story 2.1 will modify: Database schema (new user table)

5. **Error Handling and Validation**
   - Ensure DATABASE_URL is set in .env
   - Ensure PostgreSQL container is running before migration
   - Handle case where table already exists (migration idempotency)
   - Test migration rollback works correctly

### Architecture Alignment

**From architecture.md - Database Models Section:**

```python
# Architecture specifies this exact structure
class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: str
    birth_date: date
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
```

**Relationships (Future Stories):**
- `numerology_profile: Optional["NumerologyProfile"]` - Epic 4
- `conversations: List["Conversation"]` - Epic 3
- `oauth_accounts: List["OAuthAccount"]` - Story 2.11 (Google/Apple OAuth)

**Naming Conventions (From architecture.md):**
- ✅ Table name: `user` (singular, snake_case)
- ✅ Columns: `snake_case` (email, full_name, birth_date)
- ✅ Boolean: `is_active` (prefix with is_)
- ✅ Timestamps: `created_at`, `updated_at` (suffix with _at)
- ✅ Foreign keys: `{table}_id` (not applicable yet)

### Key Design Decisions

**1. UUID as Primary Key:**
- UUIDs provide globally unique identifiers
- Prevents enumeration attacks (can't guess user IDs)
- Safe for distributed systems (no collision risk)
- Trade-off: Larger than integer IDs (16 bytes vs 4-8 bytes)

**2. Email as Unique Identifier:**
- Email used for login (username = email)
- Unique constraint prevents duplicate accounts
- Index on email for fast login queries
- Case sensitivity: PostgreSQL is case-sensitive by default
  - Consider: Future story may add lowercase normalization

**3. Hashed Password (Nullable for OAuth):**
- **NEVER** store plain text passwords
- Use bcrypt with cost factor 12 (Story 2.2 will implement)
- hashed_password field stores bcrypt output (60 characters)
- Password verification happens in auth service (Story 2.4)
- **Nullable:** Set to NULL for OAuth users (Google/Apple sign-in)
- OAuth authentication will be handled via separate OAuthAccount table (Story 2.11)

**4. Birth Date as Date (not DateTime):**
- Numerology calculations only need date (year, month, day)
- Time of day not relevant for numerology
- Simpler validation and storage

**5. Soft Delete with is_active:**
- is_active=False acts as soft delete
- Preserves data for audit/GDPR compliance
- Allows reactivation if user returns
- Hard delete will be Story 7.3 (GDPR Right to be Forgotten)

**6. Timestamps with UTC:**
- `datetime.utcnow()` ensures consistent timezone handling
- All timestamps in UTC
- Frontend converts to user's local timezone
- Prevents daylight saving issues

### Prerequisites Verification

**Must be complete before starting this story:**
- [x] Story 1.2: Backend with FastAPI (FastAPI app running)
- [x] Story 1.4: Docker Compose (PostgreSQL container available)
- [x] Story 1.5: Database Connection & First Migration (Alembic configured)
- [x] Story 1.7: Makefile (make db-* commands available)

All prerequisites are complete ✅

### Testing Strategy

**Test Sequence:**
1. **Model Creation**: Create User model file, verify imports work
2. **Model Registration**: Import in __init__.py, verify Alembic can discover
3. **Migration Generation**: Run alembic autogenerate, review migration file
4. **Migration Application**: Run alembic upgrade head, verify success
5. **Database Verification**: Use psql to verify table structure
6. **CRUD Operations**: Test create, read, update, delete via Python shell
7. **Constraint Testing**: Test unique email constraint
8. **Rollback Testing**: Test alembic downgrade, then re-upgrade

**Expected Outcomes:**
- User model file exists and imports cleanly
- Alembic migration generates successfully
- Migration applies without errors
- `psql \dt` shows user table
- `psql \d user` shows correct column structure
- Email uniqueness constraint works (duplicate insert fails)
- Can query users via SQLModel select statements
- Migration is reversible (downgrade removes table)

### Potential Issues and Solutions

**Issue 1: Alembic Can't Find Model**
- **Symptom**: `alembic revision --autogenerate` doesn't detect User model
- **Solution**: Ensure User imported in models/__init__.py
- **Verification**: `python -c "from src.models import User; print(User.__tablename__)"`

**Issue 2: Migration Has No Unique Constraint**
- **Symptom**: Generated migration missing `sa.UniqueConstraint('email')`
- **Solution**: Verify `unique=True` in Field definition
- **Verification**: Check migration file content manually

**Issue 3: PostgreSQL Connection Error**
- **Symptom**: `could not connect to server` during migration
- **Solution**: Start PostgreSQL: `docker-compose up -d postgres` or `make docker-up`
- **Verification**: `docker ps` shows postgres container running

**Issue 4: Datetime Timezone Issues**
- **Symptom**: Timestamps show incorrect timezone
- **Solution**: Always use `datetime.utcnow()` not `datetime.now()`
- **Verification**: Insert test user, check created_at is UTC

**Issue 5: UUID Import Error**
- **Symptom**: `NameError: name 'uuid4' is not defined`
- **Solution**: Import uuid4: `from uuid import uuid4`
- **Verification**: Python shell test: `from uuid import uuid4; print(uuid4())`

### Database Schema Diagram

```
┌─────────────────────────────────────────────────┐
│                    user                         │
├─────────────────────────────────────────────────┤
│ id                UUID         PRIMARY KEY      │
│ email             VARCHAR      UNIQUE, INDEXED  │
│ hashed_password   VARCHAR      NULLABLE         │
│ full_name         VARCHAR      NOT NULL         │
│ birth_date        DATE         NOT NULL         │
│ created_at        TIMESTAMP    NOT NULL         │
│ updated_at        TIMESTAMP    NOT NULL         │
│ is_active         BOOLEAN      DEFAULT TRUE     │
└─────────────────────────────────────────────────┘

Note: hashed_password is NULL for OAuth users (Story 2.11)
Future relationship: oauth_accounts (1:many)
```

### References

- [Source: docs/epics.md#Epic-2-Story-2.1] - Original story requirements
- [Source: docs/architecture.md#Database-Models] - User model specification
- [Source: docs/stories/1-5-database-connection-first-migration.md] - Database setup context
- [Source: docs/stories/1-7-makefile-development-workflow.md] - Makefile commands for migrations

---

## Dev Agent Record

### Context Reference

- docs/stories/2-1-user-model-database-schema.context.xml

### Agent Model Used

{{agent_model_name_version}}

### Debug Log

<!-- Implementation notes will be added here during development -->

### Completion Notes List

<!-- Will be populated during implementation with:
- User model creation confirmation
- Migration generation output
- Database verification results
- CRUD testing results
- Any issues encountered and resolved
-->

### File List

<!-- Will be populated with files created/modified during implementation:
- CREATED: backend/src/models/user.py
- MODIFIED: backend/src/models/__init__.py
- CREATED: backend/alembic/versions/[hash]_create_users_table.py
- MODIFIED: docs/architecture.md (if needed)
-->

---

## Definition of Done

- [ ] All acceptance criteria met
- [ ] All tasks completed
- [ ] User model created in `backend/src/models/user.py`
- [ ] User model imported in `backend/src/models/__init__.py`
- [ ] Alembic migration generated for users table
- [ ] Migration applied successfully: `alembic upgrade head`
- [ ] Database table verified: `psql \dt` shows `user` table
- [ ] All 8 columns present with correct types and constraints
- [ ] Email has unique constraint and index
- [ ] Can create, query, update users via SQLModel
- [ ] Email uniqueness constraint enforced (duplicate fails)
- [ ] Migration is reversible: `alembic downgrade -1` works
- [ ] Documentation updated (architecture.md if needed)
- [ ] No errors or warnings during migration
- [ ] Git commit created with message: "Story 2.1: User Model & Database Schema - Implementation Complete"

---

## Testing Checklist

### Test Scenario 1: Model Creation and Import
- [ ] Create `backend/src/models/user.py` with User model
- [ ] Import User in `backend/src/models/__init__.py`
- [ ] Run: `python -c "from src.models.user import User; print(User)"`
- [ ] Verify no import errors
- [ ] Verify User.__tablename__ == "user"

### Test Scenario 2: Migration Generation
- [ ] Ensure PostgreSQL running: `docker ps | grep postgres`
- [ ] Run: `cd backend && alembic revision --autogenerate -m "create users table"`
- [ ] Verify migration file created in `backend/alembic/versions/`
- [ ] Open migration file and verify:
  - [ ] `op.create_table('user', ...)` present
  - [ ] All 8 columns defined
  - [ ] Unique constraint on email
  - [ ] Index on email

### Test Scenario 3: Migration Application
- [ ] Run: `cd backend && alembic upgrade head`
- [ ] Verify output contains "Running upgrade" message
- [ ] No errors in output
- [ ] Run: `alembic current`
- [ ] Verify current migration is "create users table"

### Test Scenario 4: Database Verification
- [ ] Connect: `docker exec -it numerologist-postgres psql -U postgres -d numerologist`
- [ ] Run: `\dt` - verify `user` table listed
- [ ] Run: `\d user` - verify all columns present:
  - [ ] id uuid (primary key)
  - [ ] email character varying (unique, indexed)
  - [ ] hashed_password character varying
  - [ ] full_name character varying
  - [ ] birth_date date
  - [ ] created_at timestamp
  - [ ] updated_at timestamp
  - [ ] is_active boolean
- [ ] Run: `\di` - verify `ix_user_email` index exists
- [ ] Exit psql

### Test Scenario 5: CRUD Operations
- [ ] Open Python shell: `cd backend && python`
- [ ] Import and create user:
  ```python
  from src.models.user import User
  from datetime import date
  from uuid import uuid4

  user = User(
      email="test@example.com",
      hashed_password="fake_hash",
      full_name="Test User",
      birth_date=date(1990, 1, 1)
  )
  print(f"User ID: {user.id}")
  print(f"Created at: {user.created_at}")
  print(f"Is active: {user.is_active}")
  ```
- [ ] Verify id, created_at, updated_at, is_active auto-populated
- [ ] Test unique email constraint (try duplicate email insert)

### Test Scenario 6: Migration Rollback
- [ ] Run: `cd backend && alembic downgrade -1`
- [ ] Verify output shows downgrade message
- [ ] Connect to psql, run `\dt` - verify `user` table removed
- [ ] Run: `alembic upgrade head`
- [ ] Verify user table recreated
- [ ] Verify migration is fully reversible

---

## Change Log

| Version | Date       | Author | Changes |
|---------|------------|--------|---------|
| 1.0     | 2025-11-05 | SM     | Initial story draft - User model and database schema implementation |

---

**Ready for Development:** Yes
**Blocked By:** None (All prerequisites complete)
**Blocking:** Stories 2.2-2.10 (all Epic 2 stories depend on User model)
