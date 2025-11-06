# Story 2.11 Setup & Integration Guide

## Overview

This guide covers setting up Google OAuth for Story 2.11 implementation. Google OAuth enables users to sign in with their Google account without creating a separate password.

## Prerequisites

- Backend API running (`make dev` from root)
- Mobile app development environment set up (Expo)
- Google Cloud Console account access
- Android device or emulator for testing

## Backend Setup

### 1. Google Cloud Console Configuration

#### Create OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing
3. Enable Google+ API
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
5. Choose **Web application** type
6. Add authorized redirect URIs:
   - `http://localhost:3000` (local development)
   - Your production backend URL

#### Get Client IDs

You'll need two Client IDs:

**Web Client ID** (for backend token verification):
- This is the Web OAuth Client ID you just created
- Used in `GOOGLE_WEB_CLIENT_ID` environment variable
- Located in Credentials page

**Android Client ID** (for mobile app):
- Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
- Choose **Android** type
- Add your Android package name and signing certificate SHA-1
- This is used in `google-services.json` (auto-configured by Expo)

### 2. Backend Environment Variables

Create or update `.env` in `/backend` directory:

```env
# Google OAuth Configuration
GOOGLE_WEB_CLIENT_ID=your-web-client-id-here.apps.googleusercontent.com
```

The `GOOGLE_ANDROID_CLIENT_ID` is automatically configured by Expo through Google Cloud Console.

### 3. Verify Backend Setup

```bash
# From backend directory
cd backend

# Ensure google-auth is installed
uv sync

# Test OAuth service import
python -c "from src.services.oauth_service import verify_google_token; print('✓ OAuth service loaded')"

# Run backend
make dev
```

## Frontend Setup

### 1. Mobile Environment Variables

Create or update `.env` in `/mobile` directory:

```env
# Google OAuth Configuration
EXPO_PUBLIC_GOOGLE_WEB_CLIENT_ID=your-web-client-id-here.apps.googleusercontent.com
```

**Important**: Frontend uses Web Client ID (not Android Client ID) for verification.

### 2. Verify Frontend Setup

```bash
# From mobile directory
cd mobile

# Ensure Google Sign-In SDK is installed
npm list @react-native-google-signin/google-signin

# Start Expo
npm start

# On Android emulator: press 'a'
# Expo handles Google Sign-In configuration automatically
```

### 3. Testing Locally

#### On Android Emulator

```bash
cd mobile
npm run android
```

The emulator must have Google Play Services installed (most do by default).

#### On Physical Android Device

1. Device must have Google account configured
2. Google Play Services must be installed
3. App must be properly signed (Expo handles this for dev builds)

## Testing the OAuth Flow

### Manual Integration Test

#### Backend Test

```bash
# Get a valid Google ID token (from frontend or use test token)
# Test the endpoint

curl -X POST http://localhost:8000/api/v1/auth/google \
  -H "Content-Type: application/json" \
  -d '{
    "id_token": "your-test-google-id-token"
  }'

# Expected response (200):
{
  "user": {
    "id": "uuid-here",
    "email": "user@gmail.com",
    "full_name": "User Name",
    "birth_date": "2000-01-01",
    "created_at": "2025-11-06T...",
    "updated_at": "2025-11-06T...",
    "is_active": true
  },
  "access_token": "jwt-token-here",
  "token_type": "bearer"
}
```

#### Frontend Test

1. Open app on Android device/emulator
2. Navigate to login screen
3. Tap "Sign in with Google" button
4. Follow Google authentication flow
5. Should be automatically redirected to home screen
6. User profile should show in profile screen

### Three User Linking Cases

#### Case 1: New User

1. Use Google account that hasn't signed up
2. Click "Sign in with Google"
3. New user created with placeholder birth_date (2000-01-01)
4. Prompt user to update profile with actual birth date

**Database check**:
```sql
SELECT * FROM oauthaccount WHERE provider = 'google';
```

#### Case 2: Existing OAuth User

1. Sign in with same Google account twice
2. Should work without issues
3. No duplicate OAuth accounts created

**Database check**:
```sql
SELECT COUNT(*) FROM oauthaccount WHERE provider = 'google' AND provider_user_id = 'USER_ID';
-- Should return 1 (not duplicated)
```

#### Case 3: Linking to Existing Email/Password User

1. Create user with email `user@gmail.com` and password
2. Later, sign in with Google using same email
3. Google account automatically linked to existing user
4. User can now login with either method

**Database check**:
```sql
SELECT * FROM oauthaccount WHERE provider_email = 'user@gmail.com';
```

## Database Schema Reference

### OAuthAccount Table

```sql
CREATE TABLE oauthaccount (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL FOREIGN KEY REFERENCES user(id) ON DELETE CASCADE,
  provider VARCHAR NOT NULL,
  provider_user_id VARCHAR NOT NULL,
  provider_email VARCHAR NOT NULL,
  access_token VARCHAR,
  refresh_token VARCHAR,
  token_expires_at TIMESTAMP,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

  UNIQUE(provider, provider_user_id),
  INDEX(user_id)
);
```

### User Model Changes

- `hashed_password` is nullable (NULL for OAuth users)
- `oauth_accounts` relationship added to User model

## API Endpoint Reference

### POST /api/v1/auth/google

Authenticate with Google OAuth ID token.

**Request:**
```json
{
  "id_token": "google-jwt-token-from-frontend"
}
```

**Response (200):**
```json
{
  "user": {
    "id": "uuid",
    "email": "user@gmail.com",
    "full_name": "User Name",
    "birth_date": "2000-01-01",
    "created_at": "2025-11-06T15:30:00",
    "updated_at": "2025-11-06T15:30:00",
    "is_active": true
  },
  "access_token": "jwt-token",
  "token_type": "bearer"
}
```

**Error (401 - Invalid Token):**
```json
{
  "detail": "Invalid Google token: Token expired"
}
```

**Error (500 - Server Error):**
```json
{
  "detail": "Token verification failed"
}
```

## Troubleshooting

### Backend Errors

#### "google_web_client_id not configured"
- Solution: Add `GOOGLE_WEB_CLIENT_ID` to `.env` file in `/backend`

#### "Token verification failed"
- Check if GOOGLE_WEB_CLIENT_ID matches Google Cloud Console
- Verify Google Play Services installed (Android)
- Check network connectivity to Google API

#### "GOOGLE_WEB_CLIENT_ID has wrong audience"
- The Client ID must be for "Web application" type
- Not the Android Client ID

### Frontend Errors

#### "Google Sign-In initialization failed"
- Google Play Services not installed on emulator
- Solution: Use different emulator image with Google APIs

#### "signIn is in progress"
- Multiple clicks on button while loading
- Solution: Button automatically disabled during sign-in

#### "Cannot find EXPO_PUBLIC_GOOGLE_WEB_CLIENT_ID"
- Environment variable not set in `.env`
- Solution: Create/update `.env` in mobile directory

### User Lookup Errors

#### OAuth account email not matching database
- Google email might be different from registered email
- User can update profile after login

#### User not found after linking
- Database integrity issue
- Check CASCADE delete constraints
- Verify foreign key relationship

## Security Considerations

### Token Verification

- Always verify Google ID token on backend
- Never trust token claims without signature verification
- library handles this automatically via `google.oauth2.id_token.verify_oauth2_token`

### Credential Storage

- JWT tokens stored securely:
  - Native (iOS/Android): SecureStore (encrypted)
  - Web: localStorage (ensure HTTPS in production)

### Email Linking

- Email-based linking requires user verification
- Current implementation: Automatic linking if email matches
- Future: Add email verification step for security

## Future Enhancements

1. **Multiple OAuth Providers**: Add Apple Sign-In, Microsoft, GitHub
2. **Token Refresh**: Implement token refresh logic for long-lived sessions
3. **Unlinking**: Allow users to unlink OAuth accounts
4. **Email Verification**: Add verification step before linking to existing email
5. **Profile Sync**: Sync profile picture and name from Google on each login

## References

- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [React Native Google Sign-In Library](https://github.com/react-native-google-signin/google-signin)
- [Google Auth Python Library](https://google-auth.readthedocs.io/)
- [Expo Secure Store](https://docs.expo.dev/modules/expo-secure-store/)
