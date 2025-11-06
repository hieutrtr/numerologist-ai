# Story 2.11 - Technical Analysis Summary
## OAuth Account Model & Google Sign-In

**Analysis Date:** 2025-11-06  
**Status:** Analysis Complete - Ready for Implementation  
**Document:** `/docs/stories/2-11-auth-architecture-analysis.md` (1,105 lines)

---

## Quick Reference

### Backend Stack
- **HTTP:** FastAPI 0.109.0+
- **ORM:** SQLModel 0.0.14+
- **Auth:** python-jose 3.3.0+, bcrypt 4.1.0+
- **OAuth:** google-auth 2.25.0+ (NEW)
- **Migrations:** Alembic 1.13.0+
- **Database:** PostgreSQL 12+

### Frontend Stack
- **Framework:** React Native 0.81.5
- **State Mgmt:** Zustand 5.0.8
- **HTTP:** Axios 1.13.1
- **OAuth:** @react-native-google-signin/google-signin 11.0.0 (NEW)
- **Storage:** Expo SecureStore 15.0.7 (iOS/Android), localStorage (Web)

---

## Architecture Overview

### Current State
```
┌─────────────────────────────────────────┐
│  EXISTING AUTHENTICATION SYSTEM         │
├─────────────────────────────────────────┤
│                                         │
│  Backend:                               │
│  ├── User Model (nullable password)    │
│  ├── POST /auth/register               │
│  ├── POST /auth/login                  │
│  └── GET /auth/me (protected)          │
│                                         │
│  Frontend:                              │
│  ├── useAuthStore (Zustand)            │
│  ├── Platform-aware token storage      │
│  ├── Login screen (email/password)     │
│  └── Register screen (form)            │
│                                         │
│  Security:                              │
│  ├── bcrypt password hashing           │
│  ├── JWT tokens (HS256, 15min)         │
│  └── Bearer token authentication       │
│                                         │
└─────────────────────────────────────────┘
```

### What Needs To Be Added (Story 2.11)

**Backend (3 files):**
1. `backend/src/models/oauth_account.py` - OAuthAccount model with 10 fields
2. `backend/src/services/oauth_service.py` - verify_google_token() function
3. Update `backend/src/api/v1/endpoints/auth.py` - POST /api/v1/auth/google endpoint

**Frontend (2 files):**
1. `mobile/src/components/auth/GoogleSignInButton.tsx` - UI component
2. Update `mobile/src/stores/useAuthStore.ts` - Add googleSignIn() action

**Configuration:**
1. Update `backend/src/core/settings.py` - Add google_web_client_id, google_android_client_id
2. Update `backend/pyproject.toml` - Add google-auth dependency
3. Update `mobile/package.json` - Add @react-native-google-signin/google-signin
4. Update `mobile/app.json` - Add Expo plugin for Google Sign-In
5. Update `.env.example` - Add Google OAuth variables

**Database:**
1. Generate Alembic migration for oauth_account table
2. Apply migration (alembic upgrade head)

---

## Key Implementation Patterns

### Backend Pattern (to replicate for OAuth)

**Existing Login:**
```python
@router.post("/login", status_code=200)
async def login(credentials: UserLogin, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email.ilike(credentials.email))).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": str(user.id)})
    return {
        "user": UserResponse.model_validate(user),
        "access_token": access_token,
        "token_type": "bearer"
    }
```

**New OAuth Endpoint (same structure):**
- Receive ID token from client
- Verify with OAuthService.verify_google_token()
- Three cases: new user → create, existing OAuth → return, email match → link
- Return identical response structure
- Same error handling (401 for invalid token)

### Frontend Pattern (to replicate for OAuth)

**Existing Login Action:**
```typescript
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
}
```

**New OAuth Action (same pattern):**
- Call GoogleSignin.signIn() to get ID token
- POST to /api/v1/auth/google with {id_token}
- Store token using platform-aware storage
- Update auth state
- Error handling with user-friendly messages

---

## Critical Files Reference

### Backend Core
| File | Purpose | Key Components |
|------|---------|-----------------|
| `/backend/src/models/user.py` | User entity | id, email, hashed_password (nullable), birth_date |
| `/backend/src/models/oauth_account.py` | **NEW** OAuth entity | id, user_id, provider, provider_user_id, provider_email, tokens |
| `/backend/src/api/v1/endpoints/auth.py` | Auth endpoints | register, login, me (+ **google NEW**) |
| `/backend/src/core/security.py` | Security functions | hash_password, verify_password, create_access_token, verify_access_token |
| `/backend/src/core/settings.py` | Configuration | jwt_secret, database_url, **google_web_client_id NEW**, **google_android_client_id NEW** |
| `/backend/src/services/oauth_service.py` | **NEW** OAuth verification | verify_google_token() |
| `/backend/alembic/versions/` | Migrations | **oauth_accounts table NEW** |

### Frontend Core
| File | Purpose | Key Components |
|------|---------|-----------------|
| `/mobile/src/stores/useAuthStore.ts` | Auth state | login, register, logout, checkAuth, **googleSignIn NEW** |
| `/mobile/src/app/(auth)/login.tsx` | Login UI | Email/password form, **+ GoogleSignInButton NEW** |
| `/mobile/src/components/auth/GoogleSignInButton.tsx` | **NEW** OAuth button | Google OAuth flow, error handling, loading state |
| `/mobile/src/services/api.ts` | HTTP client | Interceptors for token, error handling |
| `/mobile/src/types/user.types.ts` | TypeScript types | User, AuthState, AuthResponse |

---

## Implementation Checklist

### Phase 1: Backend Setup
- [ ] Create `backend/src/models/oauth_account.py`
- [ ] Update `backend/src/models/__init__.py` to import OAuthAccount
- [ ] Create `backend/src/services/oauth_service.py`
- [ ] Add google-auth to `backend/pyproject.toml`
- [ ] Update `backend/src/core/settings.py` with Google client IDs
- [ ] Generate Alembic migration: `alembic revision --autogenerate -m "create oauth_accounts table"`
- [ ] Apply migration: `alembic upgrade head`
- [ ] Create POST /api/v1/auth/google endpoint in auth.py

### Phase 2: Frontend Setup
- [ ] Install: `npm install @react-native-google-signin/google-signin`
- [ ] Update `mobile/app.json` with Expo plugin
- [ ] Add Google SDK initialization to `mobile/src/app/_layout.tsx`
- [ ] Update `.env` and `.env.example` with Google client IDs
- [ ] Create `mobile/src/components/auth/GoogleSignInButton.tsx`
- [ ] Add `googleSignIn()` action to `mobile/src/stores/useAuthStore.ts`

### Phase 3: Integration
- [ ] Add GoogleSignInButton to login screen (below email/password form)
- [ ] Add "or" divider between email/password and Google button
- [ ] Test: New user flow (account created, OAuth linked)
- [ ] Test: Existing OAuth user (no duplicate created)
- [ ] Test: Email match (existing user linked to OAuth)
- [ ] Verify JWT tokens work after OAuth sign-in

### Phase 4: Testing & Validation
- [ ] Test on Android device/emulator
- [ ] Verify database records correct
- [ ] Test error cases (invalid token, network failure)
- [ ] Verify logout/re-login works
- [ ] Performance testing on slow networks

---

## Technical Gaps to Fill

### Backend Gaps
1. **OAuthAccount Model** - Stores OAuth provider data, links to User
2. **OAuth Service** - Verifies Google ID tokens using google-auth library
3. **Google Endpoint** - POST /api/v1/auth/google with three user linking cases
4. **Dependencies** - google-auth package needs to be added

### Frontend Gaps
1. **GoogleSignInButton** - Triggers OAuth flow, sends token to backend
2. **Auth Store Extension** - New googleSignIn(idToken) action
3. **Google SDK Config** - Initialization with client ID
4. **Screen Integration** - Add button to login screen

---

## Database Schema

### Current User Table
```sql
CREATE TABLE user (
    id UUID PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NULL,          -- NULL for OAuth users
    full_name VARCHAR NOT NULL,
    birth_date DATE NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    is_active BOOLEAN NOT NULL
);
```

### New OAuthAccount Table (to be created)
```sql
CREATE TABLE oauth_account (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES user(id) ON DELETE CASCADE,
    provider VARCHAR NOT NULL,              -- 'google', 'apple', etc.
    provider_user_id VARCHAR NOT NULL,      -- Google's 'sub' claim
    provider_email VARCHAR NOT NULL,
    access_token VARCHAR NULL,              -- For future API calls
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

## Environment Variables Required

### Backend (.env and settings.py)
```bash
# New - Google OAuth Web (for backend verification)
GOOGLE_WEB_CLIENT_ID=xxxx-xxxx.apps.googleusercontent.com

# New - Google OAuth Android (for React Native app)
GOOGLE_ANDROID_CLIENT_ID=yyyy-yyyy.apps.googleusercontent.com
```

### Frontend (.env)
```bash
# Existing - Backend API URL
EXPO_PUBLIC_API_URL=http://localhost:8000

# New - Google Android Client ID (Expo automatically exposes EXPO_PUBLIC_ vars)
EXPO_PUBLIC_GOOGLE_ANDROID_CLIENT_ID=yyyy-yyyy.apps.googleusercontent.com
```

---

## Security Considerations

1. **Token Verification:** Always verify Google ID token on backend (never trust client)
2. **Issuer Check:** Validate issuer is accounts.google.com
3. **Email Linking:** Only link if email matches exactly, check email_verified claim
4. **Storage:** SecureStore for iOS/Android, localStorage for Web (requires HTTPS)
5. **User Distinction:** OAuth users have NULL hashed_password, cannot login with password

---

## Response Format (Identical to Login)

```json
{
  "user": {
    "id": "uuid",
    "email": "user@gmail.com",
    "full_name": "User Name",
    "birth_date": "1990-01-15",
    "created_at": "2025-11-06T10:00:00",
    "updated_at": "2025-11-06T10:00:00"
  },
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

## Three OAuth User Cases

### Case 1: New User (No OAuth Account, No Email Match)
```
1. User signs in with Google (new email)
2. System creates new User (hashed_password = NULL)
3. System creates OAuthAccount linked to User
4. Returns JWT token + user data
```

### Case 2: Existing OAuth User (Same Google Account)
```
1. User signs in with Google (same Google account)
2. System finds OAuthAccount via (provider='google', provider_user_id)
3. Returns JWT token + existing user data (no duplicate created)
```

### Case 3: Email Match (Existing User, Different Auth Method)
```
1. User created account with email: test@gmail.com (password-based)
2. User signs in with Google using same email
3. System finds User via email match
4. System links OAuthAccount to existing User
5. Returns JWT token + existing user data
```

---

## Full Analysis Document

For complete implementation details, see:
**`/docs/stories/2-11-auth-architecture-analysis.md`** (1,105 lines)

Includes:
- 14 comprehensive sections
- Code samples for all components
- Development workflow recommendations
- Testing strategies
- Security best practices
- Integration with existing stories
- Technology stack details
- Complete implementation checklist

---

## Next Steps

1. **Review this analysis** with the development team
2. **Mark Story 2.11** as "Ready for Development" (once context approved)
3. **Begin backend implementation** with OAuthAccount model
4. **Follow the patterns** established in login/register code
5. **Test all three user linking cases** before merging to main

---

**Status:** Ready for Developer Assignment  
**Risk Level:** Low (existing patterns clearly established)  
**Estimated Scope:** 40-60 development hours (backend + frontend)

