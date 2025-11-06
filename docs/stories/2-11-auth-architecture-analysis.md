# Story 2.11 - Authentication Architecture Analysis Report

**Project:** Numerologist AI  
**Story:** 2.11 - OAuth Account Model & Google Sign-In  
**Analysis Date:** 2025-11-06  
**Status:** Ready for Technical Context Generation  

---

## Executive Summary

The Numerologist AI project has a **well-structured authentication architecture** built on modern, industry-standard patterns. The existing authentication system provides a solid foundation for adding OAuth support. This analysis identifies all key architectural components, existing patterns to follow, and specific requirements for Story 2.11 implementation.

**Key Finding:** The codebase follows a consistent, clean architecture pattern with clear separation of concerns. OAuth implementation should mirror the existing login/registration patterns.

---

## 1. BACKEND AUTHENTICATION STRUCTURE

### 1.1 Current User Model

**File:** `backend/src/models/user.py`

```
Core Fields:
├── id (UUID, primary key)
├── email (unique, indexed)
├── hashed_password (nullable - for OAuth users)
├── full_name (required)
├── birth_date (required - numerology requirement)
├── created_at (auto-timestamp)
├── updated_at (auto-timestamp)
└── is_active (soft delete flag)
```

**Key Insight:** Model already designed for OAuth with `hashed_password` nullable. Comments explicitly reference Story 2.11 OAuth support.

**Relationship:** Will need to add one-to-many relationship to OAuthAccount model (cascading delete).

### 1.2 Current Auth Routes & Endpoints

**File:** `backend/src/api/v1/endpoints/auth.py`

**Existing Endpoints:**

1. **POST /api/v1/auth/register** (status: 201 Created)
   - Validates email uniqueness
   - Hashes password with bcrypt (cost factor 12)
   - Creates User record
   - Returns JWT token + user response

2. **POST /api/v1/auth/login** (status: 200 OK)
   - Case-insensitive email lookup
   - Bcrypt password verification
   - Returns JWT token + user response
   - Security: Generic error messages (prevents email enumeration)

3. **GET /api/v1/auth/me** (protected)
   - Requires valid JWT Bearer token
   - Returns current user profile
   - Uses get_current_user dependency

**Response Pattern:**
```json
{
  "user": { UserResponse object },
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

**Pattern to Follow for OAuth:** Same response format. POST /api/v1/auth/google should return identical structure.

### 1.3 Security & Password Management

**File:** `backend/src/core/security.py`

**Functions:**
- `hash_password(password)` - bcrypt rounds=12, auto-salted
- `verify_password(plain, hashed)` - constant-time comparison
- `create_access_token(data, expires_delta)` - HS256 JWT, 15min default
- `verify_access_token(token)` - validates signature and expiration

**JWT Configuration:**
- Algorithm: HS256
- Default expiration: 15 minutes
- Payload structure: `{"sub": user_id, "exp": unix_timestamp}`
- Secret key: Loaded from settings (environment variable)

**For OAuth:** Will reuse `create_access_token()` function. No password hashing needed for OAuth users.

### 1.4 Database Models Import & Registration

**File:** `backend/src/models/__init__.py`

**Current State:**
```python
from src.models.user import User
__all__ = ["User"]
```

**Required Change for Story 2.11:**
Must import OAuthAccount to enable Alembic auto-discovery:
```python
from src.models.oauth_account import OAuthAccount
__all__ = ["User", "OAuthAccount"]
```

### 1.5 Dependency Injection for Auth

**File:** `backend/src/core/deps.py`

**Function:** `get_current_user(credentials, session)`
- Extracts Bearer token from Authorization header
- Validates JWT signature and expiration
- Queries User by ID from token
- Returns 401 if invalid/expired/not found
- Used as: `current_user: User = Depends(get_current_user)`

**Pattern:** All protected endpoints use this dependency. OAuth endpoints don't need it for verification (token is sent from client).

### 1.6 API Router Structure

**File:** `backend/src/api/v1/router.py`

**Structure:**
```
/api/v1
  /auth
    /register (POST)
    /login (POST)
    /me (GET)
    /google (POST) ← NEW for Story 2.11
```

**Implementation Pattern:** Add to auth.py router, prefix handled by main router.

---

## 2. FRONTEND AUTHENTICATION IMPLEMENTATION

### 2.1 Auth Store (State Management)

**File:** `mobile/src/stores/useAuthStore.ts`

**Technology:** Zustand (lightweight state management)

**State:**
```typescript
interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  
  // Actions
  login(email: string, password: string): Promise<void>
  register(data: RegisterData): Promise<void>
  logout(): Promise<void>
  checkAuth(): Promise<void>
}
```

**Key Features:**
- Platform-aware token storage (Zustand + platform detection)
- Automatic token restoration on app load via `checkAuth()`
- Circular dependency prevention (dynamic require of useAuthStore in api.ts)

**For OAuth:** Need to add `googleSignIn(idToken: string)` action that:
1. Calls POST /api/v1/auth/google with id_token
2. Stores returned access_token
3. Updates user state
4. Sets isAuthenticated = true

### 2.2 Token Storage Strategy

**File:** `mobile/src/stores/useAuthStore.ts` (lines 14-74)

**Platform-Aware Implementation:**
- **iOS/Android:** Expo SecureStore (encrypted, platform-native)
- **Web:** localStorage (should use HTTPS in production)

**Key:** Automatic platform detection using `Platform.OS === 'web'`

**For OAuth:** Same storage mechanism. Just different token source.

### 2.3 Login Screen Implementation

**File:** `mobile/src/app/(auth)/login.tsx`

**Features:**
- Email/password validation
- Show/hide password toggle
- Error display with red highlighting
- Loading state during submission
- Keyboard handling (next/done buttons)
- Link to register screen

**Pattern to Follow:**
1. Create GoogleSignInButton component
2. Add to login screen below email/password form
3. Same error handling pattern
4. Same loading state management

### 2.4 Register Screen Implementation

**File:** `mobile/src/app/(auth)/register.tsx`

**Features:**
- Comprehensive form validation
- Field-specific error messages
- Password confirmation validation
- Birth date picker (native mobile, HTML input on web)
- Keyboard navigation
- Loading state

**Validation Patterns to Follow:**
- Email regex: `/^[^\s@]+@[^\s@]+\.[^\s@]+$/`
- Password min length: 8 characters
- Birth date: Must be in past (not today/future)

### 2.5 API Client Configuration

**File:** `mobile/src/services/api.ts`

**Setup:**
- Base URL: `process.env.EXPO_PUBLIC_API_URL` (default: http://localhost:8000)
- Timeout: 10 seconds
- Default headers: `Content-Type: application/json`

**Request Interceptor:**
- Auto-adds Authorization header: `Bearer ${token}`
- Dynamic token fetch from auth store
- Dev logging in __DEV__ mode

**Response Interceptor:**
- Catches 401 responses → calls logout() automatically
- Network error handling with user-friendly messages
- Timeout detection

**For OAuth:** No changes needed. Token flow same as email/password.

### 2.6 User Type Definitions

**File:** `mobile/src/types/user.types.ts`

**Interfaces:**
```typescript
interface User {
  id: string (UUID)
  email: string
  full_name: string
  birth_date: string (ISO format)
  created_at: string (ISO datetime)
  updated_at: string (ISO datetime)
}

interface AuthResponse {
  user: User
  access_token: string
}

interface AuthState {
  user, token, isAuthenticated, isLoading
  login, register, logout, checkAuth
}
```

**For OAuth:** AuthResponse structure stays the same. Google endpoint returns identical response.

---

## 3. DEPENDENCIES & LIBRARIES

### 3.1 Backend Dependencies (Python)

**File:** `backend/pyproject.toml`

**Current Auth-Related Packages:**
```
fastapi>=0.109.0           # HTTP framework
sqlmodel>=0.0.14           # ORM (SQLAlchemy + Pydantic)
pydantic>=2.5.0            # Validation
python-jose[cryptography]>=3.3.0  # JWT tokens (HS256)
bcrypt>=4.1.0              # Password hashing
email-validator>=2.3.0     # Email validation
psycopg2-binary>=2.9.0     # PostgreSQL driver
alembic>=1.13.0            # Database migrations
```

**Required Addition for Story 2.11:**
```
google-auth>=2.25.0        # Google OAuth token verification
google-auth-httplib2>=0.2.0  # HTTP transport for google-auth
```

**Installation Command:**
```bash
cd backend && pip add google-auth google-auth-httplib2
# or with uv package manager:
uv pip add google-auth google-auth-httplib2
```

**Alternative:** Can use `google-auth-oauthlib` for more comprehensive OAuth handling.

### 3.2 Frontend Dependencies (React Native)

**File:** `mobile/package.json`

**Current Auth-Related Packages:**
```
axios: ^1.13.1                    # HTTP client
zustand: ^5.0.8                   # State management
expo-secure-store: ^15.0.7        # Secure token storage
expo-router: ^6.0.14              # Navigation
@react-native-community/datetimepicker: ^8.4.4
```

**Required Addition for Story 2.11:**
```json
"@react-native-google-signin/google-signin": "^11.0.0"
```

**Installation Command:**
```bash
cd mobile && npm install @react-native-google-signin/google-signin
# Configure with Expo prebuild plugin
```

**Expo Configuration Required** (app.json):
```json
{
  "plugins": [
    "@react-native-google-signin/google-signin"
  ]
}
```

---

## 4. CONFIGURATION & ENVIRONMENT VARIABLES

### 4.1 Backend Settings Structure

**File:** `backend/src/core/settings.py`

**Current Settings Pattern:**
- Loads from `.env` file
- Environment variable override capability
- Typed with Pydantic BaseSettings
- Sensible defaults for development

**Existing Auth Settings:**
```python
jwt_secret: str = "dev-secret-change-in-production..."
# 32+ character secret required
```

**Required Additions for Story 2.11:**
```python
google_web_client_id: str = ""
# Google Web Client ID for backend verification
# Format: xxxx-xxxx.apps.googleusercontent.com

google_android_client_id: str = ""  
# Google Android Client ID for React Native app
# Format: xxxx-xxxx.apps.googleusercontent.com
```

### 4.2 Environment Variables Template

**File:** `.env.example`

**Current OAuth-Related Entries:** None (must be added)

**Required Additions:**
```bash
# Google OAuth Configuration
GOOGLE_WEB_CLIENT_ID=your-web-client-id.apps.googleusercontent.com
GOOGLE_ANDROID_CLIENT_ID=your-android-client-id.apps.googleusercontent.com
```

**Frontend Environment:** Uses `EXPO_PUBLIC_` prefix (automatically exposed):
```bash
EXPO_PUBLIC_GOOGLE_ANDROID_CLIENT_ID=your-android-client-id
```

### 4.3 Google Cloud Console Setup

**Required Configuration Steps:**
1. Create/select project: "Numerologist AI"
2. Enable Google Sign-In API
3. Create OAuth 2.0 Android credentials:
   - Package name: `com.numerologist.ai` (from app.json)
   - SHA-1 fingerprint: from debug.keystore
   - Result: GOOGLE_ANDROID_CLIENT_ID

4. Create OAuth 2.0 Web credentials:
   - Application type: Web
   - No redirect URIs needed (verification only)
   - Result: GOOGLE_WEB_CLIENT_ID

5. Configure OAuth Consent Screen:
   - User type: External
   - Scopes: email, profile, openid
   - Add test users for development

---

## 5. DATABASE & MIGRATIONS

### 5.1 Migration Naming Convention

**Pattern:** `{timestamp}_{revision_id}_{descriptive_message}.py`

**Examples:**
- `55e8d1b05b94_create_users_table.py`
- `99432e13f543_initial_setup.py`

**For Story 2.11:**
```
{timestamp}_{revision_id}_create_oauth_accounts_table.py
```

**Migration Generation Command:**
```bash
cd backend && alembic revision --autogenerate -m "create oauth_accounts table"
```

### 5.2 Alembic Configuration

**File:** `backend/alembic.ini`

**Key Settings:**
- SQLAlchemy URL: Loaded from environment in `env.py`
- Auto-discovery: All models imported in `backend/src/models/__init__.py`
- Supports both upgrade and downgrade

**Expected Migration Structure:**
```python
def upgrade() -> None:
    op.create_table('oauth_account',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('provider', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        # ... more columns
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('provider', 'provider_user_id', name='uq_provider_user')
    )
    op.create_index(op.f('ix_oauth_account_user_id'), 'oauth_account', ['user_id'])
    op.create_index(op.f('ix_oauth_account_provider'), 'oauth_account', ['provider'])

def downgrade() -> None:
    op.drop_index('ix_oauth_account_provider', table_name='oauth_account')
    op.drop_index('ix_oauth_account_user_id', table_name='oauth_account')
    op.drop_table('oauth_account')
```

### 5.3 Current Database Schema

**User Table Structure:**
```sql
CREATE TABLE user (
    id UUID PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NULL,
    full_name VARCHAR NOT NULL,
    birth_date DATE NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    is_active BOOLEAN NOT NULL
);

CREATE INDEX ix_user_email ON user(email);
```

**OAuthAccount Table (To Be Created):**
```sql
CREATE TABLE oauth_account (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES user(id) ON DELETE CASCADE,
    provider VARCHAR NOT NULL,
    provider_user_id VARCHAR NOT NULL,
    provider_email VARCHAR NOT NULL,
    access_token VARCHAR NULL,
    refresh_token VARCHAR NULL,
    token_expires_at TIMESTAMP NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    CONSTRAINT uq_provider_user UNIQUE (provider, provider_user_id)
);

CREATE INDEX ix_oauth_account_user_id ON oauth_account(user_id);
CREATE INDEX ix_oauth_account_provider ON oauth_account(provider);
```

---

## 6. EXISTING PATTERNS TO FOLLOW

### 6.1 Backend Request/Response Pattern

**Pattern:** Pydantic BaseModel for request validation, response model for type safety

**Login Endpoint Example (to replicate for OAuth):**
```python
@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    credentials: UserLogin,  # Pydantic model
    session: Session = Depends(get_session)  # Dependency injection
) -> dict:  # Response typed
    # Validation, database query, token generation
    return {
        "user": UserResponse.model_validate(user),
        "access_token": access_token,
        "token_type": "bearer"
    }
```

**For OAuth Endpoint:** Mirror structure with GoogleSignInRequest model.

### 6.2 Frontend Form Validation Pattern

**Pattern:** Separate validation functions + field-level error tracking

**Example from Register Screen:**
```typescript
const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

const validateForm = (): boolean => {
  const newErrors: Record<string, string> = {};
  // Validate each field, populate newErrors
  setFieldErrors(newErrors);
  return Object.keys(newErrors).length === 0;
};
```

### 6.3 Error Handling Pattern

**Backend:** 
- 400 Bad Request: Validation/business logic failures
- 401 Unauthorized: Invalid credentials or expired token
- 500 Internal Server Error: Unexpected errors

**Frontend:**
- Extract error message from `error.response?.data?.detail`
- Show user-friendly message
- Clear error on field change

**Pattern:**
```typescript
try {
  await login(email, password);
} catch (err: any) {
  let errorMessage = 'Login failed. Please try again.';
  if (err.response?.data?.detail) {
    errorMessage = err.response.data.detail;
  }
  setError(errorMessage);
}
```

### 6.4 State Management Pattern

**Pattern:** Zustand store with async actions + platform-aware storage

**Pattern:**
```typescript
export const useAuthStore = create<AuthState>((set, get) => ({
  // State
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: true,
  
  // Async action
  login: async (email: string, password: string) => {
    try {
      set({ isLoading: true });
      const response = await apiClient.post('/api/v1/auth/login', { email, password });
      await tokenStorage.setItem(AUTH_TOKEN_KEY, response.data.access_token);
      set({
        user: response.data.user,
        token: response.data.access_token,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },
}));
```

### 6.5 TypeScript Interface Pattern

**Pattern:** Strict typing with optional fields clearly marked

**Example:**
```typescript
interface User {
  id: string;  // Required
  email: string;  // Required
  full_name: string;
  birth_date: string;  // ISO format
  created_at: string;  // ISO datetime
  updated_at: string;
}

interface RegisterData {
  email: string;
  password: string;
  full_name: string;
  birth_date: string;  // Client sends ISO date (YYYY-MM-DD)
}
```

---

## 7. TECHNICAL GAPS & MISSING PIECES FOR STORY 2.11

### 7.1 Backend Gap: OAuthAccount Model

**Status:** Defined in story (template provided) but NOT YET CREATED

**Required File:** `backend/src/models/oauth_account.py`

**Requirements:**
- Inherit from SQLModel with table=True
- Foreign key to User with CASCADE delete
- Fields: id, user_id, provider, provider_user_id, provider_email, access_token, refresh_token, token_expires_at, created_at, updated_at
- Unique constraint on (provider, provider_user_id)
- Relationship back_populate to User.oauth_accounts

### 7.2 Backend Gap: OAuth Service

**Status:** Defined in story (template provided) but NOT YET CREATED

**Required File:** `backend/src/services/oauth_service.py`

**Function:** `verify_google_token(token: str) -> dict`
- Uses google-auth library
- Verifies token signature
- Checks issuer (accounts.google.com)
- Returns dict with: sub, email, name, picture, email_verified

**Dependency:** Must add google-auth to pyproject.toml

### 7.3 Backend Gap: Google Sign-In Endpoint

**Status:** Not yet created (needs to be added to auth.py)

**Endpoint:** `POST /api/v1/auth/google`

**Request Body:**
```json
{
  "id_token": "google_jwt_token_string"
}
```

**Response:** Same as login/register
```json
{
  "user": { UserResponse },
  "access_token": "jwt_token",
  "token_type": "bearer"
}
```

**Logic:**
1. Verify Google ID token
2. Check if oauth_account exists → return user
3. Check if email matches existing user → link and return
4. Create new user + oauth_account → return

### 7.4 Frontend Gap: Google Sign-In SDK Integration

**Status:** Not yet installed or configured

**Required Package:** `@react-native-google-signin/google-signin`

**Configuration Needed:**
1. Install package
2. Add Expo plugin to app.json
3. Initialize SDK in _layout.tsx
4. Provide GOOGLE_ANDROID_CLIENT_ID

### 7.5 Frontend Gap: GoogleSignInButton Component

**Status:** Not yet created

**Required File:** `mobile/src/components/auth/GoogleSignInButton.tsx`

**Features:**
- Calls GoogleSignin.signIn()
- Gets idToken from response
- Sends to backend /auth/google
- Updates auth store on success
- Shows error alert on failure
- Loading state during flow

### 7.6 Frontend Gap: Auth Store googleSignIn Action

**Status:** Not yet added to useAuthStore

**Method Needed:**
```typescript
googleSignIn: async (idToken: string) => Promise<void>
```

**Implementation:**
1. POST to /api/v1/auth/google with { id_token: idToken }
2. Store returned access_token
3. Update user state
4. Set isAuthenticated = true

---

## 8. INTEGRATION POINTS WITH EXISTING FEATURES

### 8.1 Story 2.1: User Model (Dependency)

**Status:** Already complete ✓

**Usage:** OAuthAccount will have foreign key to User.id

**No Changes Required** - User model already nullable hashed_password

### 8.2 Story 2.2: Password Hashing (No Dependency)

**Status:** Already complete ✓

**Impact:** None. OAuth users have NULL hashed_password, so hashing not used.

### 8.3 Story 2.4: JWT Token Generation (Reuse)

**Status:** Already complete ✓

**Reuse:** `create_access_token()` function

**Usage in OAuth Endpoint:**
```python
access_token = create_access_token(data={"sub": str(user.id)})
```

### 8.4 Story 2.6: Auth Store (Extend)

**Status:** Already complete ✓

**Extension Needed:** Add `googleSignIn(idToken)` action

**No Breaking Changes** - existing methods unchanged

### 8.5 Story 2.7: Login Screen (Enhance)

**Status:** Already complete ✓

**Enhancement:** Add GoogleSignInButton component

**Integration Point:** Below email/password form with "or" divider

### 8.6 Story 2.9: Profile Screen (Prepare)

**Status:** Complete, but no OAuth support yet

**Future Enhancement:** Show OAuth provider badge (not in scope)

**Current State:** No changes needed for basic OAuth

---

## 9. KEY DECISIONS & ASSUMPTIONS

### 9.1 OAuth Provider Support

**Decision:** Start with Google only (Android priority)

**Rationale:** PRD specifies Android launch, Google is Android-native

**Future:** Apple Sign-In requires iOS integration (separate story)

### 9.2 User Linking Strategy

**Decision:** Link if email matches exactly

**Rationale:** Reduces friction for users with Google account using same email

**Assumption:** Email from Google is verified (check email_verified claim)

### 9.3 New User Birth Date

**Decision:** Create OAuth users with placeholder birth_date (2000-01-01)

**Rationale:** Birth date required for numerology but OAuth doesn't provide it

**Assumption:** User must update profile with real birth date later

### 9.4 Token Storage on Web

**Decision:** Use localStorage (secure context required, HTTPS in production)

**Rationale:** Web doesn't have secure storage access, Expo SecureStore native-only

**Assumption:** Production deployment enforces HTTPS

### 9.5 OAuth Token Refresh

**Decision:** Not implemented in MVP (Story 2.11)

**Rationale:** Google access tokens last 1 hour, user likely stays in app

**Future Enhancement:** Implement refresh token rotation for long-lived sessions

---

## 10. TECHNOLOGY CHOICES & VERSIONS

### 10.1 Backend Tech Stack

| Component | Technology | Version | Usage |
|-----------|-----------|---------|-------|
| HTTP Framework | FastAPI | >=0.109.0 | REST API |
| ORM | SQLModel | >=0.0.14 | Database models & queries |
| Validation | Pydantic | >=2.5.0 | Request/response validation |
| Authentication | python-jose | >=3.3.0 | JWT tokens |
| Password Hash | bcrypt | >=4.1.0 | Password hashing |
| OAuth Verification | google-auth | >=2.25.0 | (NEW) Google token verification |
| Database | PostgreSQL | (via psycopg2) | Persistence |
| Migrations | Alembic | >=1.13.0 | Schema versioning |

### 10.2 Frontend Tech Stack

| Component | Technology | Version | Usage |
|-----------|-----------|---------|-------|
| Framework | React Native | 0.81.5 | Mobile UI |
| State Mgmt | Zustand | ^5.0.8 | Auth state |
| HTTP Client | Axios | ^1.13.1 | API calls |
| Router | Expo Router | ^6.0.14 | Navigation |
| OAuth | @react-native-google-signin/google-signin | ^11.0.0 | (NEW) Google auth |
| Token Storage | expo-secure-store | ^15.0.7 | Secure storage |
| Date Picker | @react-native-community/datetimepicker | ^8.4.4 | Date selection |

### 10.3 Database Version

**PostgreSQL:** 12+ (typical production deployment)

**Testing:** Docker container via docker-compose.yml

---

## 11. DEVELOPMENT WORKFLOW RECOMMENDATIONS

### 11.1 Backend Implementation Order

1. **Create OAuthAccount Model** (backend/src/models/oauth_account.py)
   - Define fields and relationships
   - Import in models/__init__.py

2. **Generate Migration** (alembic revision --autogenerate)
   - Review auto-generated migration
   - Apply to database (alembic upgrade head)
   - Test rollback/re-apply

3. **Add Google Auth Dependencies** (pyproject.toml)
   - google-auth >=2.25.0
   - Run: pip install or uv pip add

4. **Implement OAuth Service** (backend/src/services/oauth_service.py)
   - verify_google_token() function
   - Add GOOGLE_WEB_CLIENT_ID to settings

5. **Create Google Sign-In Endpoint** (backend/src/api/v1/endpoints/auth.py)
   - GoogleSignInRequest Pydantic model
   - POST /api/v1/auth/google handler
   - Test all three cases (new user, existing OAuth, email match)

### 11.2 Frontend Implementation Order

1. **Install Google Sign-In Package**
   - npm install @react-native-google-signin/google-signin
   - Add Expo plugin to app.json

2. **Configure Google Sign-In SDK** (mobile/src/app/_layout.tsx)
   - Initialize with GOOGLE_ANDROID_CLIENT_ID
   - Verify initialization succeeds

3. **Create GoogleSignInButton Component** (mobile/src/components/auth/GoogleSignInButton.tsx)
   - Implement Google OAuth flow
   - Call backend /auth/google
   - Handle success/error cases

4. **Extend Auth Store** (mobile/src/stores/useAuthStore.ts)
   - Add googleSignIn(idToken) action
   - Follow existing pattern (setLoading, store token, set state)

5. **Integrate into Login Screen** (mobile/src/app/(auth)/login.tsx)
   - Add GoogleSignInButton
   - Position below email/password form
   - Add "or" divider

### 11.3 Testing Checklist

**Backend:**
- [ ] OAuthAccount table created with correct schema
- [ ] Foreign key constraint enforces CASCADE delete
- [ ] Unique constraint on (provider, provider_user_id)
- [ ] OAuthService.verify_google_token() validates real tokens
- [ ] Google endpoint creates new user when no email match
- [ ] Google endpoint links existing user when email matches
- [ ] Google endpoint returns existing user for repeat OAuth login
- [ ] JWT tokens work after OAuth sign-in

**Frontend:**
- [ ] Google Sign-In SDK initializes without errors
- [ ] GoogleSignInButton triggers OAuth flow
- [ ] ID token successfully sent to backend
- [ ] Auth store updated with returned token and user
- [ ] Navigation to home screen on success
- [ ] Error message shown on failure
- [ ] Loading state visible during authentication

---

## 12. SECURITY CONSIDERATIONS FOR STORY 2.11

### 12.1 Token Verification

**Required:**
- Always verify Google ID token on backend (never trust client)
- Check issuer: must be accounts.google.com or https://accounts.google.com
- Verify audience (aud claim) matches GOOGLE_WEB_CLIENT_ID
- Check email_verified claim for safety

**Implementation:** google-auth library handles most automatically

### 12.2 Token Storage

**Secure:**
- iOS/Android: Expo SecureStore (encrypted)
- Web: localStorage only, requires HTTPS in production

**Avoid:**
- Never store tokens in AsyncStorage (unencrypted)
- Never log tokens to console in production

### 12.3 User Linking

**Safe:**
- Only link if email matches exactly
- Check email_verified claim from Google
- Log OAuth account linking for audit trail

**Dangerous:**
- Auto-linking without email verification
- Allowing unverified emails to be linked

### 12.4 Password vs OAuth Users

**Distinction:**
- Password users: hashed_password NOT NULL
- OAuth users: hashed_password IS NULL

**Implication:**
- OAuth users cannot login with password
- OAuth users must sign in via Google
- No password reset email needed for OAuth users

### 12.5 Future Security Enhancements (Out of Scope)

- Token refresh rotation (OAuth tokens refresh every 1 hour)
- Token encryption at rest in database
- Rate limiting on token verification endpoint
- Audit logging for OAuth operations
- User consent/confirmation for email linking

---

## 13. COMPREHENSIVE IMPLEMENTATION CHECKLIST

### 13.1 Backend Implementation

- [ ] OAuthAccount model created with all 10 fields
- [ ] User model updated with oauth_accounts relationship
- [ ] OAuthAccount imported in models/__init__.py
- [ ] Migration generated and applied
- [ ] google-auth added to pyproject.toml
- [ ] OAuthService.verify_google_token() implemented
- [ ] GOOGLE_WEB_CLIENT_ID added to settings.py
- [ ] GOOGLE_WEB_CLIENT_ID added to .env.example
- [ ] POST /api/v1/auth/google endpoint created
- [ ] GoogleSignInRequest Pydantic model defined
- [ ] GoogleSignInResponse Pydantic model defined
- [ ] Three OAuth cases handled (new, existing, email match)
- [ ] Database queries work for all OAuth operations
- [ ] Error handling for invalid tokens (400/401)

### 13.2 Frontend Implementation

- [ ] @react-native-google-signin/google-signin installed
- [ ] Expo plugin added to app.json
- [ ] GoogleSignin SDK initialized in _layout.tsx
- [ ] GOOGLE_ANDROID_CLIENT_ID in .env
- [ ] GoogleSignInButton component created
- [ ] Google OAuth flow implemented in component
- [ ] Backend /api/v1/auth/google call works
- [ ] Auth store googleSignIn() action added
- [ ] Auth store action stores token securely
- [ ] Auth store action updates user state
- [ ] GoogleSignInButton integrated in login screen
- [ ] "Or" divider added between email/password and Google button
- [ ] Error handling shows user-friendly message
- [ ] Loading state visible during authentication
- [ ] Navigation to home on successful sign-in

### 13.3 Testing

- [ ] OAuthAccount migration reversible (upgrade/downgrade)
- [ ] OAuthAccount table has correct constraints
- [ ] verify_google_token() accepts valid tokens
- [ ] verify_google_token() rejects invalid tokens
- [ ] New user OAuth creates correct database records
- [ ] Existing OAuth user returns without duplicate
- [ ] Email match linking works correctly
- [ ] JWT tokens valid after OAuth sign-in
- [ ] Google Sign-In button works on Android device
- [ ] Error toast shown on sign-in failure
- [ ] User can logout and re-login with Google
- [ ] Database records match expectations

### 13.4 Documentation

- [ ] Story 2.11 marked as "Ready for Development"
- [ ] All AC (Acceptance Criteria) met and verified
- [ ] All Tasks completed
- [ ] architecture.md updated with OAuth flow
- [ ] README updated with OAuth setup instructions
- [ ] .env.example has Google OAuth variables
- [ ] Dev notes included with Google Cloud Console setup steps

---

## 14. REFERENCE MATERIALS & DOCUMENTATION

### 14.1 Key Files Location

**Backend:**
- User Model: `/backend/src/models/user.py`
- Auth Endpoints: `/backend/src/api/v1/endpoints/auth.py`
- Security Utilities: `/backend/src/core/security.py`
- Settings: `/backend/src/core/settings.py`
- Dependencies: `/backend/src/core/deps.py`
- Database Config: `/backend/src/core/database.py`
- Models Init: `/backend/src/models/__init__.py`

**Frontend:**
- Auth Store: `/mobile/src/stores/useAuthStore.ts`
- User Types: `/mobile/src/types/user.types.ts`
- Login Screen: `/mobile/src/app/(auth)/login.tsx`
- Register Screen: `/mobile/src/app/(auth)/register.tsx`
- API Client: `/mobile/src/services/api.ts`

**Configuration:**
- Backend PyProject: `/backend/pyproject.toml`
- Frontend Package: `/mobile/package.json`
- Env Template: `/.env.example`
- Alembic Config: `/backend/alembic.ini`
- App Config: `/mobile/app.json`

### 14.2 Story Documentation

- Story 2.11 File: `/docs/stories/2-11-oauth-account-model-google-signin.md`
- Epic 2 File: `/docs/epics.md` (search for "Epic 2")
- Architecture: `/docs/architecture.md`

### 14.3 External Resources

**Google OAuth:**
- Google Cloud Console: https://console.cloud.google.com
- Google Sign-In Docs: https://developers.google.com/identity/protocols/oauth2
- google-auth Python: https://google-auth.readthedocs.io

**React Native Google Sign-In:**
- Package: https://github.com/react-native-google-signin/google-signin
- Docs: https://react-native-google-signin.github.io/docs/install

---

## CONCLUSION

The Numerologist AI project has a **clean, well-documented authentication architecture** that follows modern best practices. The existing patterns for email/password authentication should be directly replicated for OAuth implementation. The codebase is well-positioned for Story 2.11, with the main work being:

1. **Backend:** Create OAuthAccount model, OAuth service, and Google sign-in endpoint
2. **Frontend:** Install Google SDK, create GoogleSignInButton component, extend auth store
3. **Configuration:** Add Google credentials to environment variables

All existing patterns are clear and consistent, making implementation straightforward for a developer familiar with the codebase.

**Recommendation:** Follow the exact response structure and error handling patterns established in the login/register endpoints. This will ensure OAuth feels like a natural extension of existing authentication.

