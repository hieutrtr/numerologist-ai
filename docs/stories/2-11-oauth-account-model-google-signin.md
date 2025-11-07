# Story 2.11: OAuth Account Model & Google Sign-In

**Epic:** Epic 2 - User Authentication & Profile
**Story ID:** 2-11-oauth-account-model-google-signin
**Status:** done
**Created:** 2025-11-05
**Updated:** 2025-11-05

---

## User Story

**As a** Android user,
**I want** to sign in with my Google account,
**So that** I can quickly access the app without creating a separate password.

---

## Business Value

Reduces friction for Android users by enabling Google OAuth sign-in, which is the preferred authentication method on Android. Users can authenticate with their existing Google account, eliminating the need to remember another password. This improves conversion rates for registration and reduces support requests for password resets.

**Key Benefits:**
- Faster onboarding (1-tap sign-in vs form filling)
- Higher conversion rates (industry avg: 30-50% improvement)
- Better security (Google handles authentication)
- Reduced password fatigue for users
- Android platform best practice compliance

---

## Acceptance Criteria

### AC1: OAuthAccount Model Created
- [ ] File `backend/src/models/oauth_account.py` exists
- [ ] `OAuthAccount` class defined inheriting from `SQLModel` with `table=True`
- [ ] Foreign key `user_id` references `user.id` with CASCADE on delete
- [ ] Fields: `id`, `user_id`, `provider`, `provider_user_id`, `provider_email`, `access_token`, `refresh_token`, `token_expires_at`, `created_at`, `updated_at`
- [ ] Unique constraint on (`provider`, `provider_user_id`) to prevent duplicate OAuth accounts
- [ ] Index on `user_id` for fast lookups

### AC2: OAuthAccount Model Registered with Alembic
- [ ] OAuthAccount imported in `backend/src/models/__init__.py`
- [ ] Model discoverable by Alembic auto-generation
- [ ] SQLModel relationship established: `User.oauth_accounts` and `OAuthAccount.user`

### AC3: Alembic Migration Generated for OAuth Accounts
- [ ] Migration created: `alembic revision --autogenerate -m "create oauth_accounts table"`
- [ ] Migration file contains `create_table('oauth_account')`
- [ ] Foreign key constraint on `user_id`
- [ ] Unique constraint on `(provider, provider_user_id)`
- [ ] Index on `user_id`
- [ ] Migration is reversible (downgrade drops table)

### AC4: Migration Applied Successfully
- [ ] `alembic upgrade head` executes without errors
- [ ] Database shows `oauth_account` table: `\dt` in psql
- [ ] `\d oauth_account` shows correct columns and constraints
- [ ] Foreign key relationship to `user` table verified

### AC5: Google OAuth Verification Utility Created
- [ ] File `backend/src/services/oauth_service.py` exists
- [ ] Function `verify_google_token(id_token: str) -> dict` implemented
- [ ] Uses `google.auth.transport.requests` and `google.oauth2.id_token` for verification
- [ ] Returns user info: `{'sub', 'email', 'name', 'picture'}` on success
- [ ] Raises `ValueError` with clear message on invalid token
- [ ] Handles network errors and timeout gracefully

### AC6: Google Sign-In Backend Endpoint Created
- [ ] Endpoint `POST /api/v1/auth/google` exists in `backend/src/api/routes/auth.py`
- [ ] Accepts request body: `{"id_token": "google_jwt_token"}`
- [ ] Verifies Google ID token using oauth_service
- [ ] Checks if OAuth account exists for `provider='google'` and `provider_user_id`
- [ ] If exists: Returns JWT tokens for existing user
- [ ] If not exists but email matches: Links OAuth account to existing user
- [ ] If not exists and no email match: Creates new user + OAuth account
- [ ] Returns same response as `/auth/login`: `{"access_token", "refresh_token", "token_type", "user"}`
- [ ] Error handling: Invalid token returns 401, server errors return 500

### AC7: Database Queries for OAuth Operations
- [ ] Can query OAuth account by provider + provider_user_id
- [ ] Can query all OAuth accounts for a user
- [ ] Can create OAuth account linked to user
- [ ] Can update OAuth tokens (access_token, refresh_token, expires_at)
- [ ] Can delete OAuth account (cascade deletes when user deleted)

### AC8: Frontend Google Sign-In Button (React Native)
- [ ] Google Sign-In SDK integrated: `@react-native-google-signin/google-signin`
- [ ] Google Sign-In button component created in `mobile/src/components/auth/GoogleSignInButton.tsx`
- [ ] Button triggers Google OAuth flow via SDK
- [ ] On success: Sends ID token to `POST /api/v1/auth/google`
- [ ] On backend success: Stores tokens in auth store (Zustand)
- [ ] On backend success: Navigates to home screen
- [ ] Error handling: Shows toast with user-friendly error message

### AC9: Google OAuth Configuration
- [ ] Google Cloud Console project configured with OAuth 2.0 credentials
- [ ] Android OAuth client ID added to `.env`: `GOOGLE_ANDROID_CLIENT_ID`
- [ ] Web OAuth client ID added for backend verification: `GOOGLE_WEB_CLIENT_ID`
- [ ] Authorized redirect URIs configured (if needed for web testing)
- [ ] Google Sign-In SDK initialized in `mobile/src/app/_layout.tsx`

### AC10: Integration Testing
- [ ] Can sign in with Google on Android device/emulator
- [ ] First-time OAuth creates new user with NULL hashed_password
- [ ] Second-time OAuth returns existing user
- [ ] Existing email/password user can link Google OAuth
- [ ] JWT tokens work correctly after Google sign-in
- [ ] User profile shows correct name and email from Google
- [ ] Logout works correctly for OAuth users

---

## Tasks

### Task 1: Create OAuthAccount Model
**Mapped to:** AC1, AC2
- [ ] Create `backend/src/models/oauth_account.py`
- [ ] Define OAuthAccount class with SQLModel
- [ ] Add all 10 fields with proper types and constraints
- [ ] Define foreign key relationship to User
- [ ] Add unique constraint on (provider, provider_user_id)
- [ ] Import in `backend/src/models/__init__.py`
- [ ] Add SQLModel relationships in User and OAuthAccount models

### Task 2: Generate and Apply OAuth Migration
**Mapped to:** AC3, AC4
- [ ] Run: `make db-migrate MSG="create oauth_accounts table"`
- [ ] Review migration file for correctness
- [ ] Run: `make db-upgrade`
- [ ] Verify table created: `psql \dt`
- [ ] Verify foreign key constraint: `psql \d oauth_account`
- [ ] Test migration rollback: `make db-downgrade`
- [ ] Re-apply: `make db-upgrade`

### Task 3: Implement Google Token Verification Service
**Mapped to:** AC5
- [ ] Install Google auth library: `google-auth` in pyproject.toml
- [ ] Create `backend/src/services/oauth_service.py`
- [ ] Implement `verify_google_token(id_token: str) -> dict`
- [ ] Add GOOGLE_WEB_CLIENT_ID to settings.py
- [ ] Test with valid/invalid Google tokens
- [ ] Add error handling and logging

### Task 4: Create Google Sign-In Backend Endpoint
**Mapped to:** AC6, AC7
- [ ] Add endpoint to `backend/src/api/routes/auth.py`
- [ ] Implement request/response models (Pydantic)
- [ ] Verify Google ID token
- [ ] Check if OAuth account exists (query by provider + provider_user_id)
- [ ] Handle three cases:
  - Existing OAuth account → return tokens
  - Email matches existing user → link OAuth + return tokens
  - New user → create user + OAuth account + return tokens
- [ ] Generate JWT tokens (reuse existing token generation from login)
- [ ] Test all three cases manually

### Task 5: Configure Google OAuth in Google Cloud Console
**Mapped to:** AC9
- [ ] Create/select project in Google Cloud Console
- [ ] Enable Google Sign-In API
- [ ] Create OAuth 2.0 credentials (Android)
- [ ] Create OAuth 2.0 credentials (Web) for backend
- [ ] Configure authorized domains
- [ ] Add client IDs to `.env.example` and `.env`
- [ ] Document setup process in Dev Notes

### Task 6: Install and Configure Google Sign-In SDK (Frontend)
**Mapped to:** AC8, AC9
- [ ] Install: `npm install @react-native-google-signin/google-signin`
- [ ] Configure in `mobile/app.json` (Expo config plugin)
- [ ] Initialize SDK in `_layout.tsx` with GOOGLE_ANDROID_CLIENT_ID
- [ ] Test SDK initialization (no errors)

### Task 7: Create Google Sign-In Button Component
**Mapped to:** AC8
- [ ] Create `mobile/src/components/auth/GoogleSignInButton.tsx`
- [ ] Implement Google OAuth flow using SDK
- [ ] Call backend `POST /api/v1/auth/google` with ID token
- [ ] Update auth store with returned tokens and user
- [ ] Navigate to home screen on success
- [ ] Show error toast on failure
- [ ] Add loading state during authentication

### Task 8: Integrate Google Sign-In into Login Screen
**Mapped to:** AC8
- [ ] Add GoogleSignInButton to login screen
- [ ] Position below email/password form
- [ ] Add "or" divider
- [ ] Style to match design (Google branding guidelines)
- [ ] Test on Android device/emulator

### Task 9: Integration and End-to-End Testing
**Mapped to:** AC10
- [ ] Test new user flow: Google Sign-In → Account created → Home screen
- [ ] Test existing OAuth user: Sign in again → Same user
- [ ] Test email match: Create user with email → Sign in with Google (same email) → Linked
- [ ] Test profile screen shows correct Google info
- [ ] Test logout and re-login with Google
- [ ] Verify database records created correctly
- [ ] Test error cases (invalid token, network failure)

### Task 10: Documentation
**Mapped to:** All
- [ ] Update architecture.md with OAuth flow diagram
- [ ] Document Google Cloud Console setup steps
- [ ] Add API endpoint documentation
- [ ] Update README with OAuth setup instructions
- [ ] Document any deviations or edge cases

---

## Technical Implementation

### OAuthAccount Model Structure

**File: backend/src/models/oauth_account.py**

```python
"""
OAuth Account Model

Stores OAuth authentication data for third-party sign-in providers (Google, Apple).
Each OAuth account is linked to a User via foreign key. A user can have multiple
OAuth providers (e.g., both Google and Apple).
"""

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User


class OAuthAccount(SQLModel, table=True):
    """
    OAuth account for third-party authentication providers.

    Links external OAuth providers (Google, Apple) to internal User accounts.
    Stores OAuth tokens for potential future API calls to provider services.

    Unique constraint on (provider, provider_user_id) ensures one OAuth account
    per provider per external user.
    """

    # Primary key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique identifier for OAuth account"
    )

    # Foreign key to User
    user_id: UUID = Field(
        foreign_key="user.id",
        ondelete="CASCADE",
        description="User this OAuth account belongs to"
    )

    # OAuth provider fields
    provider: str = Field(
        index=True,
        description="OAuth provider name: 'google', 'apple', etc."
    )
    provider_user_id: str = Field(
        description="User ID from OAuth provider (Google: 'sub', Apple: 'sub')"
    )
    provider_email: str = Field(
        description="Email from OAuth provider (may differ from User.email)"
    )

    # OAuth tokens (optional, for future API integration)
    access_token: Optional[str] = Field(
        default=None,
        description="OAuth access token (encrypted in production)"
    )
    refresh_token: Optional[str] = Field(
        default=None,
        description="OAuth refresh token (encrypted in production)"
    )
    token_expires_at: Optional[datetime] = Field(
        default=None,
        description="When the access token expires"
    )

    # Metadata
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When OAuth account was linked"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last time OAuth account was updated"
    )

    # Relationship to User
    user: "User" = Relationship(back_populates="oauth_accounts")

    # Table configuration
    class Config:
        # Unique constraint: one OAuth account per provider per user
        __table_args__ = (
            {"comment": "OAuth accounts for third-party authentication"},
        )


# Unique constraint defined separately for better Alembic detection
__table_args__ = (
    UniqueConstraint("provider", "provider_user_id", name="uq_provider_user"),
)
```

**Update User Model:**

```python
# In backend/src/models/user.py
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .oauth_account import OAuthAccount

class User(SQLModel, table=True):
    # ... existing fields ...

    # Relationships
    oauth_accounts: List["OAuthAccount"] = Relationship(
        back_populates="user",
        cascade_delete=True
    )
```

### OAuth Service

**File: backend/src/services/oauth_service.py**

```python
"""
OAuth Service

Handles verification of OAuth tokens from third-party providers (Google, Apple).
"""

from google.oauth2 import id_token
from google.auth.transport import requests
from typing import Dict

from ..core.settings import settings


class OAuthService:
    """Service for OAuth token verification and user info extraction."""

    @staticmethod
    def verify_google_token(token: str) -> Dict[str, str]:
        """
        Verify Google ID token and extract user information.

        Args:
            token: Google ID token (JWT) from client

        Returns:
            dict: User info with keys: 'sub', 'email', 'name', 'picture'

        Raises:
            ValueError: If token is invalid or verification fails

        Example:
            user_info = OAuthService.verify_google_token(id_token)
            print(user_info['email'])  # user@gmail.com
        """
        try:
            # Verify token with Google
            idinfo = id_token.verify_oauth2_token(
                token,
                requests.Request(),
                settings.google_web_client_id
            )

            # Verify issuer
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Invalid issuer')

            # Extract user info
            return {
                'sub': idinfo['sub'],  # Google user ID
                'email': idinfo['email'],
                'name': idinfo.get('name', ''),
                'picture': idinfo.get('picture', ''),
                'email_verified': idinfo.get('email_verified', False)
            }

        except ValueError as e:
            raise ValueError(f"Invalid Google token: {str(e)}")
        except Exception as e:
            raise ValueError(f"Token verification failed: {str(e)}")
```

### Google Sign-In Backend Endpoint

**File: backend/src/api/routes/auth.py (add to existing file)**

```python
from pydantic import BaseModel
from fastapi import HTTPException
from sqlmodel import Session, select

from ...models.user import User
from ...models.oauth_account import OAuthAccount
from ...services.oauth_service import OAuthService
from ...core.database import get_session
from datetime import date


class GoogleSignInRequest(BaseModel):
    id_token: str


class GoogleSignInResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


@router.post("/google", response_model=GoogleSignInResponse)
async def google_sign_in(
    request: GoogleSignInRequest,
    session: Session = Depends(get_session)
):
    """
    Sign in or register with Google OAuth.

    Flow:
    1. Verify Google ID token
    2. Check if OAuth account exists → return existing user
    3. Check if email matches existing user → link OAuth
    4. Otherwise → create new user + OAuth account

    Returns JWT tokens and user info (same as /login).
    """
    try:
        # Verify Google token
        google_user = OAuthService.verify_google_token(request.id_token)

    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

    # Check if OAuth account already exists
    oauth_account = session.exec(
        select(OAuthAccount)
        .where(OAuthAccount.provider == "google")
        .where(OAuthAccount.provider_user_id == google_user['sub'])
    ).first()

    if oauth_account:
        # Existing OAuth user - return tokens
        user = oauth_account.user
        access_token, refresh_token = create_tokens(user.id)

        return GoogleSignInResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserResponse.from_orm(user)
        )

    # Check if user exists with this email
    existing_user = session.exec(
        select(User).where(User.email == google_user['email'])
    ).first()

    if existing_user:
        # Link OAuth to existing user
        oauth_account = OAuthAccount(
            user_id=existing_user.id,
            provider="google",
            provider_user_id=google_user['sub'],
            provider_email=google_user['email']
        )
        session.add(oauth_account)
        session.commit()

        user = existing_user
    else:
        # Create new user + OAuth account
        # Default birth_date for OAuth users (will be updated in profile)
        new_user = User(
            email=google_user['email'],
            full_name=google_user['name'],
            hashed_password=None,  # NULL for OAuth users
            birth_date=date(2000, 1, 1)  # Placeholder
        )
        session.add(new_user)
        session.flush()  # Get user.id

        oauth_account = OAuthAccount(
            user_id=new_user.id,
            provider="google",
            provider_user_id=google_user['sub'],
            provider_email=google_user['email']
        )
        session.add(oauth_account)
        session.commit()

        user = new_user

    # Generate JWT tokens
    access_token, refresh_token = create_tokens(user.id)

    return GoogleSignInResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.from_orm(user)
    )
```

### Frontend Google Sign-In Button

**File: mobile/src/components/auth/GoogleSignInButton.tsx**

```typescript
import React, { useState } from 'react';
import { TouchableOpacity, Text, ActivityIndicator, Alert } from 'react-native';
import { GoogleSignin, statusCodes } from '@react-native-google-signin/google-signin';
import { useAuthStore } from '@/stores/authStore';
import { router } from 'expo-router';

export function GoogleSignInButton() {
  const [loading, setLoading] = useState(false);
  const { googleSignIn } = useAuthStore();

  const handleGoogleSignIn = async () => {
    try {
      setLoading(true);

      // Check if Google Play Services are available
      await GoogleSignin.hasPlayServices();

      // Sign in with Google
      const userInfo = await GoogleSignin.signIn();
      const idToken = userInfo.idToken;

      if (!idToken) {
        throw new Error('No ID token received from Google');
      }

      // Send ID token to backend
      await googleSignIn(idToken);

      // Navigate to home on success
      router.replace('/');

    } catch (error: any) {
      console.error('Google Sign-In Error:', error);

      if (error.code === statusCodes.SIGN_IN_CANCELLED) {
        // User cancelled sign-in
      } else if (error.code === statusCodes.IN_PROGRESS) {
        Alert.alert('Sign-In In Progress', 'Please wait...');
      } else if (error.code === statusCodes.PLAY_SERVICES_NOT_AVAILABLE) {
        Alert.alert('Error', 'Google Play Services not available');
      } else {
        Alert.alert('Sign-In Failed', error.message || 'Unable to sign in with Google');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <TouchableOpacity
      onPress={handleGoogleSignIn}
      disabled={loading}
      style={{
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: '#fff',
        padding: 12,
        borderRadius: 8,
        borderWidth: 1,
        borderColor: '#ddd',
      }}
    >
      {loading ? (
        <ActivityIndicator size="small" color="#4285F4" />
      ) : (
        <>
          {/* Google Logo */}
          <Text style={{ fontSize: 16, marginLeft: 8, color: '#000' }}>
            Sign in with Google
          </Text>
        </>
      )}
    </TouchableOpacity>
  );
}
```

**Update Auth Store:**

```typescript
// mobile/src/stores/authStore.ts
export const useAuthStore = create<AuthStore>((set) => ({
  // ... existing state and methods ...

  googleSignIn: async (idToken: string) => {
    try {
      const response = await api.post('/auth/google', { id_token: idToken });
      const { access_token, refresh_token, user } = response.data;

      // Store tokens
      await SecureStore.setItemAsync('access_token', access_token);
      await SecureStore.setItemAsync('refresh_token', refresh_token);

      set({ user, isAuthenticated: true });
    } catch (error) {
      console.error('Google sign-in error:', error);
      throw error;
    }
  },
}));
```

---

## Dev Notes

### Expo Custom Dev Client Requirement

**Important:** Google Sign-In requires **Expo Custom Dev Client**, not Expo Go.

**Why?** The `@react-native-google-signin/google-signin` library uses native modules that are not available in Expo Go.

**Setup Options:**

1. **Android Device (Recommended for Development):**
   ```bash
   cd mobile
   eas build --platform android --profile preview
   # Scan QR code with device or emulator
   ```

2. **Android Emulator:**
   ```bash
   eas build --platform android --profile preview
   # Build will provide installation instructions
   ```

3. **Local Development (Requires Android NDK):**
   ```bash
   cd mobile
   expo run:android
   # This builds a dev client locally
   ```

**Web/iOS:** Google Sign-In button will show a message: "Google Sign-In not available. Please use a custom Expo dev client." (Feature requires native module).

### Google Cloud Console Setup

**Step-by-Step Configuration:**

1. **Create/Select Project:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create new project or select existing: "Numerologist AI"

2. **Enable Google Sign-In API:**
   - Navigate to "APIs & Services" → "Library"
   - Search for "Google Sign-In API"
   - Click "Enable"

3. **Create OAuth 2.0 Credentials (Android):**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - Application type: "Android"
   - Package name: `com.numerologist.ai` (from app.json)
   - SHA-1: Get from `keytool -list -v -keystore ~/.android/debug.keystore`
   - Save Android Client ID to `.env`: `GOOGLE_ANDROID_CLIENT_ID`

4. **Create OAuth 2.0 Credentials (Web - for backend):**
   - Click "Create Credentials" → "OAuth client ID"
   - Application type: "Web application"
   - Name: "Numerologist AI Backend"
   - No redirect URIs needed (we only verify tokens)
   - Save Web Client ID to `.env`: `GOOGLE_WEB_CLIENT_ID`

5. **Configure OAuth Consent Screen:**
   - Go to "OAuth consent screen"
   - User type: "External"
   - App name: "Numerologist AI"
   - Support email: your email
   - Scopes: email, profile, openid
   - Add test users (for development)

### Settings Configuration

**backend/src/core/settings.py:**

```python
class Settings(BaseSettings):
    # ... existing settings ...

    # OAuth Configuration
    google_web_client_id: str = ""
    """Google Web Client ID for backend token verification"""

    google_android_client_id: str = ""
    """Google Android Client ID for React Native app"""
```

**.env.example:**

```bash
# Google OAuth
GOOGLE_WEB_CLIENT_ID=your-web-client-id.apps.googleusercontent.com
GOOGLE_ANDROID_CLIENT_ID=your-android-client-id.apps.googleusercontent.com
```

### Security Considerations

1. **Token Storage:**
   - Never store Google ID tokens in database
   - Access/refresh tokens encrypted at rest (future enhancement)
   - Use secure storage on mobile (Expo SecureStore)

2. **Token Verification:**
   - Always verify ID token on backend (don't trust client)
   - Check issuer and audience (iss, aud claims)
   - Verify email_verified flag

3. **User Linking:**
   - Only link if email matches exactly
   - Consider email verification flag
   - Log OAuth account creation for audit

### Testing Strategy

**Manual Testing Checklist:**

1. **New User Flow:**
   - Click "Sign in with Google"
   - Select Google account
   - Verify account created in database
   - Check user.hashed_password is NULL
   - Check oauth_account record created
   - Verify JWT tokens work

2. **Existing OAuth User:**
   - Sign out
   - Sign in with Google again
   - Should use existing account (no duplicate)

3. **Email Match Linking:**
   - Create user with email/password: test@gmail.com
   - Sign in with Google using test@gmail.com
   - Verify OAuth account linked to existing user
   - Verify no duplicate user created

4. **Error Cases:**
   - Invalid ID token → 401 error
   - Network failure → Graceful error message
   - Google Play Services unavailable → Clear message

### Database Schema Updates

**Migration Expected Output:**

```sql
CREATE TABLE oauth_account (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    provider VARCHAR NOT NULL,
    provider_user_id VARCHAR NOT NULL,
    provider_email VARCHAR NOT NULL,
    access_token VARCHAR,
    refresh_token VARCHAR,
    token_expires_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    CONSTRAINT uq_provider_user UNIQUE (provider, provider_user_id)
);

CREATE INDEX ix_oauth_account_user_id ON oauth_account(user_id);
CREATE INDEX ix_oauth_account_provider ON oauth_account(provider);
```

### Integration with Existing Stories

**Dependencies:**
- Story 2.1: User model must be created first (foreign key target)
- Story 2.2: Password hashing NOT required (OAuth users have NULL password)
- Story 2.4: JWT token generation logic will be reused
- Story 2.6: Auth store will be extended with googleSignIn method
- Story 2.7: Login screen will add Google Sign-In button

**Impact on Other Stories:**
- Story 2.3 (Registration): No changes needed
- Story 2.4 (Login): Login endpoint unchanged (email/password still works)
- Story 2.5 (Get User): Works for both OAuth and password users
- Story 2.9 (Profile): May need to show OAuth provider badge

### Future Enhancements (Post-MVP)

1. **Apple Sign-In** (Required for iOS):
   - Similar OAuthAccount structure
   - Provider = 'apple'
   - Different SDK and verification

2. **Account Unlinking:**
   - Allow users to disconnect OAuth providers
   - Ensure at least one auth method remains

3. **Multiple OAuth Providers:**
   - User can link both Google and Apple
   - Choose preferred sign-in method

4. **OAuth Token Refresh:**
   - Store and refresh access tokens
   - Use for future Google API integration

5. **Profile Picture Sync:**
   - Store Google profile picture URL
   - Display in profile screen

---

## Definition of Done

- [ ] All acceptance criteria met
- [ ] All tasks completed
- [ ] OAuthAccount model created in `backend/src/models/oauth_account.py`
- [ ] OAuthAccount imported in `backend/src/models/__init__.py`
- [ ] Alembic migration generated and applied for oauth_accounts table
- [ ] Foreign key relationship User ↔ OAuthAccount works
- [ ] Google token verification service implemented
- [ ] `POST /api/v1/auth/google` endpoint works
- [ ] Three OAuth cases handled: new user, existing OAuth, email match
- [ ] Google Sign-In SDK configured in React Native
- [ ] GoogleSignInButton component created and integrated
- [ ] Can sign in with Google on Android device
- [ ] Database records correct (user, oauth_account)
- [ ] JWT tokens work after Google sign-in
- [ ] Error handling works for all failure cases
- [ ] Documentation updated (architecture.md, README.md)
- [ ] Git commit: "Story 2.11: OAuth Account Model & Google Sign-In - Implementation Complete"

---

## Testing Checklist

### Test Scenario 1: OAuthAccount Model and Migration
- [ ] Create OAuthAccount model with all fields
- [ ] Generate migration: `make db-migrate MSG="create oauth_accounts table"`
- [ ] Apply migration: `make db-upgrade`
- [ ] Verify table: `psql \dt` shows `oauth_account`
- [ ] Verify foreign key: `psql \d oauth_account`
- [ ] Test rollback: `make db-downgrade`
- [ ] Re-apply: `make db-upgrade`

### Test Scenario 2: Google Token Verification
- [ ] Get valid Google ID token (test account)
- [ ] Call `OAuthService.verify_google_token(token)`
- [ ] Verify returns dict with 'sub', 'email', 'name'
- [ ] Test with invalid token → raises ValueError
- [ ] Test with expired token → raises ValueError

### Test Scenario 3: Google Sign-In - New User
- [ ] Start with empty database (no users)
- [ ] POST /api/v1/auth/google with valid ID token
- [ ] Verify response: access_token, refresh_token, user
- [ ] Verify database: user created with NULL hashed_password
- [ ] Verify database: oauth_account created with provider='google'
- [ ] Test JWT token works: GET /api/v1/users/me

### Test Scenario 4: Google Sign-In - Existing OAuth User
- [ ] Create user + OAuth account in database
- [ ] POST /api/v1/auth/google with same Google account
- [ ] Verify returns existing user (no duplicate)
- [ ] Verify no new oauth_account created

### Test Scenario 5: Google Sign-In - Email Match Linking
- [ ] Create user with email/password: test@gmail.com
- [ ] POST /api/v1/auth/google with Google account (test@gmail.com)
- [ ] Verify OAuth account linked to existing user
- [ ] Verify no duplicate user created
- [ ] Verify can still login with email/password

### Test Scenario 6: Frontend Google Sign-In Button
- [ ] Open login screen on Android device/emulator
- [ ] Click "Sign in with Google" button
- [ ] Google account picker appears
- [ ] Select account
- [ ] Navigates to home screen
- [ ] Profile shows correct Google name and email

### Test Scenario 7: End-to-End Integration
- [ ] Sign in with Google (new user)
- [ ] Verify home screen loads
- [ ] Navigate to profile screen
- [ ] Verify name and email from Google
- [ ] Logout
- [ ] Sign in with Google again
- [ ] Verify same user (no duplicate)

### Test Scenario 8: Error Handling
- [ ] Test invalid ID token → Shows error message
- [ ] Test network failure → Shows error message
- [ ] Test Google Play Services unavailable → Shows clear message
- [ ] Test cancelling Google sign-in → No error, returns to login

---

## Change Log

| Version | Date       | Author | Changes |
|---------|------------|--------|---------|
| 1.0     | 2025-11-05 | SM     | Initial story draft - OAuth Account model and Google Sign-In integration |

---

**Ready for Development:** No (Draft - Needs Context Generation)
**Blocked By:** Story 2.1 (User model must exist first)
**Blocking:** None (Optional enhancement for Epic 2)
**Priority:** High (Required for Android launch per PRD)
