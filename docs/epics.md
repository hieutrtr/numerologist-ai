# Numerologist AI - Epic Breakdown

**Author:** Hieu
**Date:** 2025-11-04
**Project Level:** 2 (Medium Complexity)
**Target Scale:** 1,000-10,000 users (MVP → Growth)

---

## Overview

This document provides the detailed epic breakdown for Numerologist AI, expanding on the requirements in the [PRD](./PRD.md) and guided by the [Architecture](./architecture.md).

Each epic includes:
- Expanded goal and value proposition
- Complete story breakdown with user stories
- Acceptance criteria for each story
- Story sequencing and dependencies
- Testable outcomes

**Epic Sequencing Principles:**
- Each epic delivers a complete, testable vertical slice
- Frontend and backend work together within each epic
- Stories are sequentially ordered with clear dependencies
- Every epic ends with something you can demo

**Technology Context:**
- Monorepo structure: `backend/` (Python + uv) and `mobile/` (React Native + Expo)
- Backend: FastAPI + PostgreSQL + Redis + Pipecat-ai (managed by uv)
- Frontend: React Native + Expo (Web PWA + Android)
- Voice Pipeline: Deepgram + Azure OpenAI GPT-5-mini + ElevenLabs + Daily.co

---

## Epic 1: Foundation & Project Setup

**Goal:** Establish development environment with backend and frontend talking to each other

**Business Value:** Enables all future development, proves technical stack works end-to-end

**Testable Outcome:** Run `make dev` → Backend API at localhost:8000 → Mobile app connects and displays API status

**Prerequisites:** None (first epic)

**Estimated Effort:** 1-2 days

---

### Story 1.1: Initialize Monorepo Structure

**As a** developer,
**I want** a clean monorepo structure with backend and mobile folders,
**So that** I can organize code logically and get started with development.

**Acceptance Criteria:**
1. Root directory `numerologist-ai/` created with proper structure
2. `.gitignore` configured for Python (`__pycache__`, `*.pyc`, `.env`) and Node.js (`node_modules/`, `.expo/`)
3. `README.md` with project overview and setup instructions
4. Git repository initialized with initial commit
5. Directory structure matches architecture document

**Technical Notes:**
```
numerologist-ai/                    # Root
├── backend/                        # Python + uv (to be created in Story 1.2)
├── mobile/                         # React Native + Expo (to be created in Story 1.3)
├── docker-compose.yml              # To be created in Story 1.4
├── Makefile                        # To be created in Story 1.7
├── .gitignore
└── README.md
```

Create folders: `backend/`, `mobile/`, root-level files
Use standard .gitignore templates for Python and React Native

**Prerequisites:** None

---

### Story 1.2: Setup Backend with uv & FastAPI

**As a** backend developer,
**I want** a uv-managed FastAPI project with fast dependency management,
**So that** I can start building API endpoints with a solid foundation.

**Acceptance Criteria:**
1. `backend/` folder initialized with uv (`uv init`)
2. `pyproject.toml` configured with FastAPI, Uvicorn, SQLModel, Alembic
3. Dependencies organized: main dependencies + optional dev dependencies
4. `src/` folder structure created: `main.py`, `api/`, `core/`, `models/`, `services/`
5. Basic FastAPI app in `src/main.py` with root endpoint
6. `uv sync` installs all dependencies successfully
7. `uv run uvicorn src.main:app --reload` starts server at localhost:8000
8. Visiting `http://localhost:8000` returns `{"message": "Numerologist AI API"}`
9. API docs available at `http://localhost:8000/docs`

**Technical Notes:**
```toml
# pyproject.toml
[project]
name = "numerologist-api"
version = "0.1.0"
description = "Numerologist AI Backend"
requires-python = ">=3.10"
dependencies = [
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
    "sqlmodel>=0.0.14",
    "alembic>=1.13.0",
    "pydantic>=2.5.0",
    "python-jose[cryptography]>=3.3.0",
    "bcrypt>=4.1.0",
    "redis>=5.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "black>=24.1.0",
    "ruff>=0.1.0",
]

[tool.uv]
dev-dependencies = [
    "pytest>=7.4.0",
    "black>=24.1.0",
    "ruff>=0.1.0",
]
```

**uv Commands Reference:**
```bash
uv init                    # Initialize project
uv add <package>          # Add dependency
uv add --dev <package>    # Add dev dependency
uv sync                   # Install dependencies (like poetry install)
uv run <command>          # Run command in venv (like poetry run)
uv pip list               # List installed packages
```

**Wiring Up:**
- Create `backend/src/main.py` as application entry point
- All other modules import relative to `src/` (e.g., `from src.api import router`)
- Run with: `uv run uvicorn src.main:app --reload`

**Prerequisites:** Story 1.1 complete

---

### Story 1.3: Setup Frontend with Expo TypeScript

**As a** frontend developer,
**I want** a React Native Expo app with TypeScript configured,
**So that** I can start building mobile UI with type safety.

**Acceptance Criteria:**
1. `mobile/` folder initialized with Expo TypeScript template
2. `src/` folder created with structure: `app/`, `components/`, `services/`, `stores/`, `types/`, `constants/`, `utils/`
3. `package.json` includes Expo SDK, React Native, TypeScript
4. `tsconfig.json` properly configured
5. Basic app structure with Expo Router
6. `npm install` completes successfully
7. `npm start` launches Expo dev server
8. App opens in browser (press 'w') showing "Numerologist AI" home screen
9. Hot reload works when editing code

**Technical Notes:**
```bash
cd mobile
npx create-expo-app@latest . --template blank-typescript

# Create src structure
mkdir -p src/{app,components,services,stores,types,constants,utils}
mv app/* src/app/ 2>/dev/null || true
```

**Resulting structure:**
```
mobile/
├── src/
│   ├── app/               # Expo Router (pages)
│   ├── components/        # Reusable UI components
│   ├── services/          # API clients, utilities
│   ├── stores/            # Zustand state stores
│   ├── types/             # TypeScript type definitions
│   ├── constants/         # App constants
│   └── utils/             # Helper functions
├── package.json
├── tsconfig.json
└── app.json
```

Configure `app.json` to use `src/app` as entry:
```json
{
  "expo": {
    "experiments": {
      "typedRoutes": true
    }
  }
}
```

Note: Expo Router automatically detects `src/app` directory.

**Key dependencies to add:**
- axios (API calls)
- zustand (state management)
- @react-native-async-storage/async-storage (token storage)
- expo-secure-store (secure token storage)

**Wiring Up:**
- Expo Router automatically discovers routes in `src/app/`
- Import modules: `import { Component } from '@/components/Component'` (using path alias)
- Configure tsconfig.json path aliases:
```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

**Prerequisites:** Story 1.1 complete

---

### Story 1.4: Docker Compose for Local Services

**As a** developer,
**I want** PostgreSQL and Redis running locally via Docker,
**So that** I can develop without installing databases on my machine.

**Acceptance Criteria:**
1. `docker-compose.yml` created in root directory
2. PostgreSQL service configured (port 5432, volume for data persistence)
3. Redis service configured (port 6379)
4. `.env.example` file with database connection strings
5. `.env` file created (gitignored) with actual values
6. `docker-compose up -d` starts both services successfully
7. Can connect to PostgreSQL: `psql postgresql://postgres:password@localhost:5432/numerologist`
8. Can connect to Redis: `redis-cli -h localhost -p 6379 ping` returns PONG
9. Services persist data between restarts

**Technical Notes:**
```yaml
# docker-compose.yml structure
services:
  postgres:
    image: postgres:18-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: numerologist
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

**Prerequisites:** Story 1.1 complete

---

### Story 1.5: Database Connection & First Migration

**As a** backend developer,
**I want** the FastAPI app connected to PostgreSQL with migrations working,
**So that** I can create database tables and evolve the schema.

**Acceptance Criteria:**
1. SQLModel database connection configured in `backend/src/core/database.py`
2. Database URL from environment variables
3. Alembic initialized (`alembic init alembic`)
4. Alembic configured to use SQLModel
5. First migration created (empty, just to test setup)
6. `alembic upgrade head` runs successfully
7. Health check endpoint `GET /health` returns database connection status
8. Endpoint response: `{"status": "healthy", "database": "connected"}`
9. If database down, endpoint returns proper error

**Technical Notes:**
```python
# backend/src/core/database.py
from sqlmodel import create_engine, Session
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/numerologist")

engine = create_engine(DATABASE_URL)

def get_session():
    with Session(engine) as session:
        yield session
```

**Wiring Up:**
```python
# In backend/src/main.py
from src.core.database import engine
from src.models.user import User  # Import all models

@app.on_event("startup")
async def startup():
    # Create tables on startup (dev only, use migrations in prod)
    # SQLModel.metadata.create_all(engine)
    pass
```

**Prerequisites:** Stories 1.2 and 1.4 complete

---

### Story 1.6: Frontend API Service Setup

**As a** frontend developer,
**I want** an API client configured to call the backend,
**So that** I can make HTTP requests from the mobile app.

**Acceptance Criteria:**
1. Axios installed and configured in `mobile/src/services/api.ts`
2. Base URL configured from environment (localhost:8000 for dev)
3. Request interceptors set up for future auth tokens
4. Response interceptors for error handling
5. API client exported and ready to use
6. Home screen updated to call `/health` endpoint on mount
7. Display API status on home screen: "API Status: Connected" or error message
8. Proper error handling if backend is down

**Technical Notes:**
```typescript
// mobile/src/services/api.ts
import axios from 'axios';

const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth tokens (future)
apiClient.interceptors.request.use(
  (config) => {
    // Will add auth token here later
    return config;
  },
  (error) => Promise.reject(error)
);
```

**Wiring Up:**
```typescript
// Use in components:
import { apiClient } from '@/services/api';

// Make requests:
const response = await apiClient.get('/health');
const data = await apiClient.post('/api/v1/auth/login', { email, password });
```

**Prerequisites:** Stories 1.3 and 1.5 complete

---

### Story 1.7: Makefile & Development Workflow

**As a** developer,
**I want** simple commands to start the entire development environment,
**So that** I can get coding quickly without remembering complex commands.

**Acceptance Criteria:**
1. `Makefile` created in root directory
2. `make help` shows all available commands
3. `make docker-up` starts PostgreSQL + Redis
4. `make backend` starts FastAPI server
5. `make mobile` starts Expo dev server
6. `make dev` starts everything (Docker → Backend → Mobile)
7. `make test` runs all tests (backend + mobile)
8. `make clean` cleans up temporary files
9. All commands work and have proper error messages
10. README.md documents the Makefile commands

**Technical Notes:**
```makefile
.PHONY: help dev backend mobile docker-up docker-down test clean

help:
	@echo "Numerologist AI Development Commands"
	@echo ""
	@echo "  make dev          - Start full development environment"
	@echo "  make backend      - Start backend only"
	@echo "  make mobile       - Start mobile app only"
	@echo "  make docker-up    - Start PostgreSQL + Redis"
	@echo "  make docker-down  - Stop Docker services"
	@echo "  make test         - Run all tests"
	@echo "  make clean        - Clean up generated files"

dev: docker-up
	@echo "Starting development environment..."
	@make backend & make mobile

backend:
	cd backend && uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

mobile:
	cd mobile && npm start

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

test:
	cd backend && uv run pytest
	cd mobile && npm test

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	cd mobile && rm -rf node_modules/.cache
```

**Prerequisites:** All previous stories in Epic 1 complete

---

## Epic 1 Summary

**What's Working After Epic 1:**
- ✅ Monorepo structure with backend + mobile
- ✅ Backend: FastAPI running with PostgreSQL + Redis
- ✅ Frontend: Expo app running and connecting to backend
- ✅ Simple commands to start everything: `make dev`
- ✅ End-to-end: Mobile app displays backend health status

**Demo:** Show backend API docs at `/docs` and mobile app displaying "API Status: Connected"

**Next Epic:** User Authentication & Profile

---

## Epic 2: User Authentication & Profile

**Goal:** Enable users to register, login, and manage their profiles with secure authentication

**Business Value:** Identity layer that enables personalized numerology readings and conversation history

**Testable Outcome:** User can register → login → see profile with name and birth date → logout → login again

**Prerequisites:** Epic 1 complete (backend + frontend running)

**Estimated Effort:** 2-3 days

---

### Story 2.1: User Model & Database Schema

**As a** backend developer,
**I want** a User database model with all required fields,
**So that** I can store user information securely.

**Acceptance Criteria:**
1. `User` model created in `backend/src/models/user.py` using SQLModel
2. Fields: `id` (UUID), `email` (unique), `hashed_password`, `full_name`, `birth_date`, `created_at`, `updated_at`, `is_active`
3. Email field has unique constraint and index
4. Password stored as bcrypt hash (never plain text)
5. Alembic migration created for users table
6. `alembic upgrade head` creates table successfully
7. Can verify table exists: `\dt` in psql shows `user` table

**Technical Notes:**
```python
# backend/src/models/user.py
from sqlmodel import SQLModel, Field
from datetime import date, datetime
from uuid import UUID, uuid4

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

**Wiring Up:**
```python
# Import in models/__init__.py for Alembic auto-discovery
from src.models.user import User

# Use in endpoints:
from src.models.user import User
from src.core.database import get_session
from sqlmodel import Session, select

@router.post("/endpoint")
async def create_user(session: Session = Depends(get_session)):
    user = User(email="...", ...)
    session.add(user)
    session.commit()
```

**Prerequisites:** Story 1.5 complete (database connection working)

---

### Story 2.2: Password Hashing & Security Utilities

**As a** backend developer,
**I want** secure password hashing utilities,
**So that** I can safely store and verify user passwords.

**Acceptance Criteria:**
1. Security utilities created in `backend/src/core/security.py`
2. `hash_password(password: str) -> str` function using bcrypt (cost factor 12)
3. `verify_password(plain: str, hashed: str) -> bool` function
4. `create_access_token(data: dict) -> str` function for JWT tokens
5. `verify_access_token(token: str) -> dict` function
6. JWT secret from environment variable (`JWT_SECRET`)
7. Access token expiry: 15 minutes
8. All functions have unit tests
9. Tests pass: `uv run pytest tests/test_security.py`

**Technical Notes:**
```python
# backend/src/core/security.py
import bcrypt
from jose import jwt, JWTError
from datetime import datetime, timedelta
import os

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(12)).decode()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)

def verify_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
```

**Wiring Up:**
```python
# Import in endpoints:
from src.core.security import hash_password, verify_password, create_access_token, verify_access_token

# Use when creating user:
hashed_pw = hash_password(user_data.password)

# Use when logging in:
if not verify_password(plain_password, user.hashed_password):
    raise HTTPException(401)

# Use when creating token:
token = create_access_token({"sub": str(user.id)})
```

**Prerequisites:** Story 1.2 complete (backend dependencies installed)

---

### Story 2.3: User Registration API Endpoint

**As a** user,
**I want** to register with email, password, name, and birth date,
**So that** I can create an account and access the app.

**Acceptance Criteria:**
1. Pydantic schemas created in `backend/src/schemas/user.py` (UserCreate, UserResponse)
2. Registration endpoint: `POST /api/v1/auth/register`
3. Request body: `{"email": "...", "password": "...", "full_name": "...", "birth_date": "YYYY-MM-DD"}`
4. Validates email format, password strength (min 8 chars), birth date not in future
5. Returns 400 if email already exists
6. Returns 201 with user data (no password in response) and JWT token
7. Password hashed before storing in database
8. Response format: `{"user": {...}, "access_token": "...", "token_type": "bearer"}`
9. Can test with curl or Postman
10. API docs show endpoint at `/docs`

**Technical Notes:**
```python
# backend/src/api/v1/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from backend.src.core.database import get_session
from backend.src.core.security import hash_password, create_access_token
from backend.src.models.user import User
from backend.src.schemas.user import UserCreate, UserResponse

router = APIRouter()

@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, session: Session = Depends(get_session)):
    # Check if email exists
    existing = session.exec(select(User).where(User.email == user_data.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    hashed_pw = hash_password(user_data.password)
    user = User(
        email=user_data.email,
        hashed_password=hashed_pw,
        full_name=user_data.full_name,
        birth_date=user_data.birth_date
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Create token
    token = create_access_token({"sub": str(user.id)})

    return {
        "user": UserResponse.from_orm(user),
        "access_token": token,
        "token_type": "bearer"
    }
```

**Wiring Up:**
```python
# In backend/src/api/v1/router.py
from fastapi import APIRouter
from src.api.v1.endpoints import auth

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# In backend/src/main.py
from src.api.v1.router import api_router

app = FastAPI()
app.include_router(api_router, prefix="/api/v1")
```

**Prerequisites:** Stories 2.1 and 2.2 complete

---

### Story 2.4: User Login API Endpoint

**As a** user,
**I want** to login with my email and password,
**So that** I can access my account.

**Acceptance Criteria:**
1. Login endpoint: `POST /api/v1/auth/login`
2. Request body: `{"email": "...", "password": "..."}`
3. Validates credentials against database
4. Returns 401 if email not found or password incorrect
5. Returns 200 with user data and JWT token on success
6. Response format: `{"user": {...}, "access_token": "...", "token_type": "bearer"}`
7. Token includes user ID in payload
8. Can test successful and failed login scenarios
9. Rate limiting note added (implement in Epic 7)

**Technical Notes:**
```python
@router.post("/login", response_model=dict)
async def login(credentials: UserLogin, session: Session = Depends(get_session)):
    # Find user
    user = session.exec(select(User).where(User.email == credentials.email)).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Verify password
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create token
    token = create_access_token({"sub": str(user.id)})

    return {
        "user": UserResponse.from_orm(user),
        "access_token": token,
        "token_type": "bearer"
    }
```

**Wiring Up:**
- Add to same `auth.py` router created in Story 2.3
- Already wired through `/api/v1/auth` prefix
- No additional routing needed

**Prerequisites:** Story 2.3 complete

---

### Story 2.5: Get Current User Endpoint (Protected)

**As a** logged-in user,
**I want** to retrieve my profile using my auth token,
**So that** I can display my information in the app.

**Acceptance Criteria:**
1. Dependency function `get_current_user` created that validates JWT token
2. Endpoint: `GET /api/v1/users/me`
3. Requires `Authorization: Bearer <token>` header
4. Returns 401 if token missing, invalid, or expired
5. Returns 200 with user data if token valid
6. Response: `{"id": "...", "email": "...", "full_name": "...", "birth_date": "..."}`
7. No password in response
8. Can test with valid and invalid tokens

**Technical Notes:**
```python
# backend/src/core/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
from backend.src.core.security import verify_access_token
from backend.src.core.database import get_session
from backend.src.models.user import User

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
) -> User:
    token = credentials.credentials
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("sub")
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user

# In auth.py
@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
```

**Wiring Up:**
```python
# Use get_current_user as dependency in any protected endpoint:
from src.core.deps import get_current_user
from src.models.user import User

@router.get("/protected-route")
async def protected_route(current_user: User = Depends(get_current_user)):
    # current_user is automatically available
    return {"message": f"Hello {current_user.full_name}"}
```

**Prerequisites:** Story 2.4 complete

---

### Story 2.6: Frontend Auth State Management (Zustand)

**As a** frontend developer,
**I want** centralized auth state management,
**So that** the app knows if user is logged in and can access their token.

**Acceptance Criteria:**
1. Zustand store created in `mobile/src/stores/useAuthStore.ts`
2. State: `user`, `token`, `isAuthenticated`, `isLoading`
3. Actions: `login()`, `register()`, `logout()`, `checkAuth()`
4. Token stored in Expo SecureStore (encrypted storage)
5. On app load, check SecureStore for saved token
6. If token exists, validate with `GET /users/me`
7. Store provides auth context to entire app
8. TypeScript types for User and auth state

**Technical Notes:**
```typescript
// mobile/src/stores/useAuthStore.ts
import { create } from 'zustand';
import * as SecureStore from 'expo-secure-store';
import { apiClient } from '../services/api';

interface User {
  id: string;
  email: string;
  full_name: string;
  birth_date: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;

  login: (email: string, password: string) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: true,

  login: async (email, password) => {
    try {
      const response = await apiClient.post('/api/v1/auth/login', { email, password });
      const { user, access_token } = response.data;

      await SecureStore.setItemAsync('auth_token', access_token);
      set({ user, token: access_token, isAuthenticated: true });
    } catch (error) {
      throw error;
    }
  },

  register: async (data) => {
    try {
      const response = await apiClient.post('/api/v1/auth/register', data);
      const { user, access_token } = response.data;

      await SecureStore.setItemAsync('auth_token', access_token);
      set({ user, token: access_token, isAuthenticated: true });
    } catch (error) {
      throw error;
    }
  },

  logout: async () => {
    await SecureStore.deleteItemAsync('auth_token');
    set({ user: null, token: null, isAuthenticated: false });
  },

  checkAuth: async () => {
    try {
      const token = await SecureStore.getItemAsync('auth_token');
      if (!token) {
        set({ isLoading: false });
        return;
      }

      // Validate token with backend
      const response = await apiClient.get('/api/v1/users/me', {
        headers: { Authorization: `Bearer ${token}` }
      });

      set({ user: response.data, token, isAuthenticated: true, isLoading: false });
    } catch (error) {
      await SecureStore.deleteItemAsync('auth_token');
      set({ user: null, token: null, isAuthenticated: false, isLoading: false });
    }
  },
}));
```

**Wiring Up:**
```typescript
// In any component:
import { useAuthStore } from '@/stores/useAuthStore';

function LoginScreen() {
  const { login, isLoading, error } = useAuthStore();

  const handleLogin = async () => {
    try {
      await login(email, password);
      // Store automatically updates, navigation happens via layout
    } catch (error) {
      // Handle error
    }
  };
}
```

**Update apiClient to include auth token:**
```typescript
// In mobile/src/services/api.ts - update interceptor
import { useAuthStore } from '@/stores/useAuthStore';

apiClient.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

**Prerequisites:** Story 1.6 complete (API client setup)

---

### Story 2.7: Login Screen UI

**As a** user,
**I want** a login screen where I can enter my credentials,
**So that** I can access my account.

**Acceptance Criteria:**
1. Login screen component created in `mobile/src/app/(auth)/login.tsx`
2. Form fields: Email (email input), Password (secure text input)
3. "Login" button calls `useAuthStore.login()`
4. Shows loading state while logging in
5. Displays error message if login fails
6. On success, navigates to home screen
7. "Don't have an account? Register" link to register screen
8. Proper keyboard handling (next/done buttons)
9. Email validation (format check)
10. Works on both web and mobile

**Technical Notes:**
- Use React Native TextInput components
- Add keyboard avoidance for mobile
- Show/hide password toggle
- Disable button while loading

**Wiring Up:**
```typescript
// Expo Router automatically discovers this route
// File: mobile/src/app/(auth)/login.tsx
// Route: accessible at /login when not authenticated

// In mobile/src/app/_layout.tsx:
import { Stack } from 'expo-router';

export default function Layout() {
  return (
    <Stack>
      <Stack.Screen name="(auth)" options={{ headerShown: false }} />
    </Stack>
  );
}
```

**Prerequisites:** Story 2.6 complete

---

### Story 2.8: Register Screen UI

**As a** new user,
**I want** a registration screen with all required fields,
**So that** I can create an account.

**Acceptance Criteria:**
1. Register screen component created in `mobile/src/app/(auth)/register.tsx`
2. Form fields: Email, Password, Confirm Password, Full Name, Birth Date
3. Birth date picker (native date picker on mobile, HTML input on web)
4. Password confirmation validation (must match)
5. "Register" button calls `useAuthStore.register()`
6. Shows loading state while registering
7. Displays error message if registration fails (e.g., email exists)
8. On success, navigates to home screen (auto-logged in)
9. "Already have an account? Login" link to login screen
10. Form validation before submission

**Technical Notes:**
```typescript
// Validation checks
- Email: valid format
- Password: min 8 characters
- Password confirmation: matches password
- Full name: not empty
- Birth date: valid date, not in future
```

**Wiring Up:**
- Same as login screen - Expo Router auto-discovers
- Link between screens using Expo Router Link:
```typescript
import { Link } from 'expo-router';

<Link href="/register">Don't have an account? Register</Link>
<Link href="/login">Already have an account? Login</Link>
```

**Prerequisites:** Story 2.6 complete

---

### Story 2.9: Profile Screen UI

**As a** logged-in user,
**I want** to view my profile information,
**So that** I can see my account details.

**Acceptance Criteria:**
1. Profile screen created in `mobile/src/app/(tabs)/profile.tsx`
2. Displays user information: Name, Email, Birth Date
3. Shows formatted birth date (e.g., "May 15, 1990")
4. "Logout" button that calls `useAuthStore.logout()`
5. On logout, clears token and navigates to login screen
6. Loading state while fetching user data
7. Error handling if user data fails to load
8. Clean, readable layout

**Technical Notes:**
- Use date-fns for date formatting
- Simple card-based layout
- Logout button in prominent position

**Wiring Up:**
```typescript
// File: mobile/src/app/(tabs)/profile.tsx
// Automatically part of tabs navigation

// In mobile/src/app/(tabs)/_layout.tsx:
import { Tabs } from 'expo-router';

export default function TabsLayout() {
  return (
    <Tabs>
      <Tabs.Screen name="index" options={{ title: 'Conversation' }} />
      <Tabs.Screen name="history" options={{ title: 'History' }} />
      <Tabs.Screen name="profile" options={{ title: 'Profile' }} />
    </Tabs>
  );
}
```

**Prerequisites:** Stories 2.7 and 2.8 complete

---

### Story 2.10: Auth Navigation Flow

**As a** user,
**I want** automatic navigation based on auth status,
**So that** I'm directed to login or home screen appropriately.

**Acceptance Criteria:**
1. Root layout checks auth status on app load
2. If not authenticated → show auth screens (login/register)
3. If authenticated → show main tabs (home, history, profile)
4. Protected screens require authentication
5. After login/register → automatic navigation to home
6. After logout → automatic navigation to login
7. Deep linking respects auth state
8. Smooth transitions (no flashing of wrong screen)
9. Works correctly on app reload

**Technical Notes:**
```typescript
// mobile/src/app/_layout.tsx
export default function RootLayout() {
  const { isAuthenticated, isLoading, checkAuth } = useAuthStore();

  useEffect(() => {
    checkAuth();
  }, []);

  if (isLoading) {
    return <LoadingScreen />;
  }

  return (
    <Stack>
      {!isAuthenticated ? (
        <Stack.Screen name="(auth)" />
      ) : (
        <Stack.Screen name="(tabs)" />
      )}
    </Stack>
  );
}
```

**Wiring Up:**
```typescript
// This is the ROOT layout that controls everything
// File: mobile/src/app/_layout.tsx

// Import auth store at app initialization:
import { useAuthStore } from '@/stores/useAuthStore';
import { useEffect } from 'react';

// The layout checks auth and shows appropriate screens
// No manual navigation needed - layout handles it automatically based on isAuthenticated state
```

**Prerequisites:** Story 2.9 complete

---

## Epic 2 Summary

**What's Working After Epic 2:**
- ✅ Backend: User registration, login, profile endpoints
- ✅ Security: Password hashing, JWT tokens, protected routes
- ✅ Frontend: Login screen, register screen, profile screen
- ✅ State: Centralized auth management with Zustand
- ✅ Storage: Secure token storage with Expo SecureStore
- ✅ Navigation: Auto-redirect based on auth status

**Demo:**
1. Open app → See login screen
2. Tap "Register" → Fill form → Create account
3. Automatically logged in → See home screen
4. Navigate to Profile → See user details
5. Logout → Back to login screen
6. Login again → Successfully authenticated

**Next Epic:** Voice Infrastructure & Basic Conversation

---

## Epic 3: Voice Infrastructure & Basic Conversation

**Goal:** Enable real-time voice conversations between user and AI through Pipecat-ai pipeline

**Business Value:** Core product differentiator - voice-first numerology conversations

**Testable Outcome:** User taps "Start Conversation" → speaks into microphone → hears AI voice respond naturally

**Prerequisites:** Epic 2 complete (authenticated users)

**Estimated Effort:** 3-4 days

---

### Story 3.1: Add Voice Pipeline Dependencies

**As a** backend developer,
**I want** all voice pipeline dependencies installed,
**So that** I can build the Pipecat-ai voice bot.

**Acceptance Criteria:**
1. Add pipecat-ai with extras to pyproject.toml: `pipecat-ai[daily,deepgram,openai,elevenlabs]`
2. Add Azure OpenAI SDK
3. Add Daily.co Python SDK
4. Add Deepgram SDK v5.2.0
5. Add ElevenLabs SDK v2.17.0
6. Environment variables documented in .env.example:
   - `DAILY_API_KEY`
   - `DEEPGRAM_API_KEY`
   - `AZURE_OPENAI_API_KEY`
   - `AZURE_OPENAI_ENDPOINT`
   - `ELEVENLABS_API_KEY`
7. `uv sync` installs all dependencies successfully
8. Can import all packages without errors

**Technical Notes:**
```toml
# Add to pyproject.toml dependencies
dependencies = [
    # ... existing deps
    "pipecat-ai[daily,deepgram,openai,elevenlabs]>=0.0.30",
    "deepgram-sdk>=5.2.0",
    "elevenlabs>=2.17.0",
    "openai>=1.0.0",  # For Azure OpenAI
    "daily-python>=0.9.0",
]
```

**Prerequisites:** Story 1.2 complete (backend with uv)

---

### Story 3.2: Daily.co Room Management Service

**As a** backend developer,
**I want** a service to create and manage Daily.co rooms,
**So that** users can connect for voice conversations.

**Acceptance Criteria:**
1. Service created in `backend/src/services/daily_service.py`
2. `create_room(conversation_id: str) -> dict` function that:
   - Creates Daily.co room with unique name
   - Sets room expiry (2 hours)
   - Returns room URL and meeting token
3. `delete_room(room_name: str)` function for cleanup
4. Uses Daily.co REST API with API key from env
5. Error handling for API failures
6. Unit tests for service functions
7. Can manually test room creation with curl

**Technical Notes:**
```python
# backend/src/services/daily_service.py
import os
import httpx
from typing import Dict

DAILY_API_KEY = os.getenv("DAILY_API_KEY")
DAILY_API_URL = "https://api.daily.co/v1"

async def create_room(conversation_id: str) -> Dict[str, str]:
    """Create a Daily.co room for voice conversation"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{DAILY_API_URL}/rooms",
            headers={
                "Authorization": f"Bearer {DAILY_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "name": f"conversation-{conversation_id}",
                "properties": {
                    "exp": int(time.time()) + 7200,  # 2 hours
                    "enable_chat": False,
                    "enable_screenshare": False,
                    "enable_recording": False,
                }
            }
        )
        response.raise_for_status()
        data = response.json()

        # Create meeting token
        token_response = await client.post(
            f"{DAILY_API_URL}/meeting-tokens",
            headers={
                "Authorization": f"Bearer {DAILY_API_KEY}",
                "Content-Type": "application/json"
            },
            json={"properties": {"room_name": data["name"]}}
        )
        token_data = token_response.json()

        return {
            "room_name": data["name"],
            "room_url": data["url"],
            "token": token_data["token"]
        }

async def delete_room(room_name: str):
    """Delete a Daily.co room"""
    async with httpx.AsyncClient() as client:
        await client.delete(
            f"{DAILY_API_URL}/rooms/{room_name}",
            headers={"Authorization": f"Bearer {DAILY_API_KEY}"}
        )
```

**Wiring Up:**
```python
# In backend/src/services/__init__.py
from src.services.daily_service import create_room, delete_room

# Use in conversation endpoints:
from src.services.daily_service import create_room
room_data = await create_room(str(conversation.id))
```

**Prerequisites:** Story 3.1 complete

---

### Story 3.3: Basic Pipecat Bot with Greeting

**As a** backend developer,
**I want** a basic Pipecat bot that can greet users via voice,
**So that** I can validate the voice pipeline works end-to-end.

**Acceptance Criteria:**
1. Pipecat bot created in `backend/src/voice_pipeline/pipecat_bot.py`
2. Bot connects to Daily.co room using DailyTransport
3. Integrates Deepgram STT (speech-to-text)
4. Integrates Azure OpenAI GPT-5-mini (simple greeting prompt for now)
5. Integrates ElevenLabs TTS (text-to-speech)
6. Pipeline processes: Audio → Deepgram → GPT → ElevenLabs → Audio
7. System prompt: "You are a friendly AI assistant. Greet the user warmly."
8. Bot runs in separate process/async task
9. Can manually test by joining room URL in browser

**Technical Notes:**
```python
# backend/src/voice_pipeline/pipecat_bot.py
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.transports.services.daily import DailyTransport, DailyParams
from pipecat.services.deepgram import DeepgramSTTService
from pipecat.services.azure import AzureOpenAILLMService
from pipecat.services.elevenlabs import ElevenLabsTTSService
from pipecat.processors.aggregators.llm_response import LLMAssistantResponseAggregator, LLMUserResponseAggregator
import os

async def run_bot(room_url: str, token: str):
    """Run Pipecat bot in Daily.co room"""

    # Daily.co transport
    transport = DailyTransport(
        room_url,
        token,
        "Numerology AI Bot",
        DailyParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            vad_enabled=True,
            vad_analyzer=SileroVADAnalyzer()
        )
    )

    # Speech-to-text
    stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"))

    # LLM
    llm = AzureOpenAILLMService(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        model="gpt-5-mini"
    )

    # Text-to-speech
    tts = ElevenLabsTTSService(
        api_key=os.getenv("ELEVENLABS_API_KEY"),
        voice_id="21m00Tcm4TlvDq8ikWAM"  # Default conversational voice
    )

    # System prompt
    messages = [
        {"role": "system", "content": "You are a friendly AI assistant. Greet the user warmly and ask how you can help them today."}
    ]

    # Build pipeline
    pipeline = Pipeline([
        transport.input(),
        stt,
        LLMUserResponseAggregator(messages),
        llm,
        tts,
        transport.output(),
        LLMAssistantResponseAggregator(messages)
    ])

    # Run
    runner = PipelineRunner()
    await runner.run(pipeline)
```

**Wiring Up:**
```python
# Import in conversation endpoint:
from src.voice_pipeline.pipecat_bot import run_bot

# Spawn bot when conversation starts:
import asyncio
asyncio.create_task(run_bot(room_url, token))

# Bot runs independently in background, connects to Daily room
```

**Prerequisites:** Story 3.2 complete

---

### Story 3.4: Conversation Model & Start Endpoint

**As a** user,
**I want** to start a voice conversation via API,
**So that** I can begin talking to the AI numerologist.

**Acceptance Criteria:**
1. `Conversation` model created in `backend/src/models/conversation.py`
2. Fields: `id`, `user_id`, `daily_room_id`, `started_at`, `ended_at`, `duration_seconds`
3. Alembic migration for conversations table
4. Endpoint: `POST /api/v1/conversations/start` (requires auth)
5. Endpoint creates Daily.co room
6. Endpoint creates Conversation record in database
7. Endpoint spawns Pipecat bot process for the room
8. Returns: `{"conversation_id": "...", "daily_room_url": "...", "daily_token": "..."}`
9. User receives room URL and token to join
10. Can test with Postman - get room URL back

**Technical Notes:**
```python
# backend/src/api/v1/endpoints/conversations.py
from fastapi import APIRouter, Depends
from backend.src.models.conversation import Conversation
from backend.src.services.daily_service import create_room
from backend.src.voice_pipeline.pipecat_bot import run_bot
from backend.src.core.deps import get_current_user
from backend.src.models.user import User
import asyncio

router = APIRouter()

@router.post("/start")
async def start_conversation(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Create conversation record
    conversation = Conversation(user_id=current_user.id)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    # Create Daily.co room
    room_data = await create_room(str(conversation.id))

    # Update conversation with room ID
    conversation.daily_room_id = room_data["room_name"]
    session.commit()

    # Spawn bot in background
    asyncio.create_task(run_bot(room_data["room_url"], room_data["token"]))

    return {
        "conversation_id": str(conversation.id),
        "daily_room_url": room_data["room_url"],
        "daily_token": room_data["token"]
    }
```

**Wiring Up:**
```python
# In backend/src/api/v1/router.py
from src.api.v1.endpoints import conversations

api_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])

# Creates route: POST /api/v1/conversations/start
```

**Prerequisites:** Stories 3.3 complete

---

### Story 3.5: Frontend Conversation State (Zustand)

**As a** frontend developer,
**I want** conversation state management,
**So that** the app can track active conversations.

**Acceptance Criteria:**
1. Zustand store created in `mobile/src/stores/useConversationStore.ts`
2. State: `conversationId`, `dailyCall`, `isConnected`, `isMicActive`, `isAISpeaking`
3. Actions: `startConversation()`, `endConversation()`, `toggleMic()`
4. `startConversation()` calls backend API, gets room URL and token
5. Store manages Daily.co call object
6. TypeScript types for conversation state

**Technical Notes:**
```typescript
// mobile/src/stores/useConversationStore.ts
import { create } from 'zustand';
import { apiClient } from '../services/api';
import DailyIframe from '@daily-co/daily-js';

interface ConversationState {
  conversationId: string | null;
  dailyCall: any | null;
  isConnected: boolean;
  isMicActive: boolean;
  isAISpeaking: boolean;
  error: string | null;

  startConversation: () => Promise<void>;
  endConversation: () => Promise<void>;
  toggleMic: () => void;
}

export const useConversationStore = create<ConversationState>((set, get) => ({
  conversationId: null,
  dailyCall: null,
  isConnected: false,
  isMicActive: false,
  isAISpeaking: false,
  error: null,

  startConversation: async () => {
    try {
      // Call backend to start conversation
      const response = await apiClient.post('/api/v1/conversations/start');
      const { conversation_id, daily_room_url, daily_token } = response.data;

      // Create Daily call
      const callFrame = DailyIframe.createCallObject();

      await callFrame.join({
        url: daily_room_url,
        token: daily_token
      });

      set({
        conversationId: conversation_id,
        dailyCall: callFrame,
        isConnected: true,
        isMicActive: true
      });
    } catch (error) {
      set({ error: error.message });
      throw error;
    }
  },

  endConversation: async () => {
    const { dailyCall, conversationId } = get();

    if (dailyCall) {
      await dailyCall.leave();
      dailyCall.destroy();
    }

    if (conversationId) {
      await apiClient.post(`/api/v1/conversations/${conversationId}/end`);
    }

    set({
      conversationId: null,
      dailyCall: null,
      isConnected: false,
      isMicActive: false
    });
  },

  toggleMic: () => {
    const { dailyCall, isMicActive } = get();
    if (dailyCall) {
      dailyCall.setLocalAudio(!isMicActive);
      set({ isMicActive: !isMicActive });
    }
  },
}));
```

**Wiring Up:**
```typescript
// Use in conversation screen:
import { useConversationStore } from '@/stores/useConversationStore';

function ConversationScreen() {
  const { startConversation, endConversation, isConnected } = useConversationStore();

  // Call startConversation() to begin
  // Store handles API call, Daily.co connection, and state updates
}
```

**Prerequisites:** Story 1.6 complete (API client)

---

### Story 3.6: Microphone Permission & Setup

**As a** user,
**I want** the app to request microphone permission,
**So that** I can speak during voice conversations.

**Acceptance Criteria:**
1. Uses Expo Audio API for microphone permissions
2. Permission requested on first conversation attempt
3. Shows clear explanation: "We need microphone access for voice conversations"
4. If denied, shows error message with settings link
5. If granted, proceeds to start conversation
6. Permission status cached (doesn't ask every time)
7. Works on both web and mobile
8. On web, uses browser's native permission prompt
9. On mobile, uses native permission dialog

**Technical Notes:**
```typescript
// mobile/src/services/audio.service.ts
import { Audio } from 'expo-av';
import { Platform } from 'react-native';

export const requestMicrophonePermission = async (): Promise<boolean> => {
  try {
    if (Platform.OS === 'web') {
      // Web uses browser permissions
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      stream.getTracks().forEach(track => track.stop());
      return true;
    } else {
      // Mobile uses Expo Audio
      const { status } = await Audio.requestPermissionsAsync();
      return status === 'granted';
    }
  } catch (error) {
    console.error('Microphone permission error:', error);
    return false;
  }
};

export const checkMicrophonePermission = async (): Promise<boolean> => {
  try {
    const { status } = await Audio.getPermissionsAsync();
    return status === 'granted';
  } catch (error) {
    return false;
  }
};
```

**Wiring Up:**
```typescript
// Use in conversation screen before starting:
import { requestMicrophonePermission } from '@/services/audio.service';

const hasPermission = await requestMicrophonePermission();
if (hasPermission) {
  await startConversation();
} else {
  // Show error message
}
```

**Prerequisites:** Story 1.3 complete (Expo app)

---

### Story 3.7: Conversation Screen UI

**As a** user,
**I want** a conversation screen with microphone button,
**So that** I can start and control voice conversations.

**Acceptance Criteria:**
1. Conversation screen created in `mobile/src/app/(tabs)/index.tsx`
2. Large central microphone button
3. Button shows different states:
   - Not connected: "Start Conversation"
   - Connecting: Loading spinner
   - Connected: Pulsing mic icon
   - AI speaking: Different visual indicator
4. Tap button to start conversation (requests mic permission first)
5. Tap again to end conversation
6. Shows connection status text
7. Clean, minimal design focused on voice interaction
8. Works on web and mobile

**Technical Notes:**
```typescript
// mobile/src/app/(tabs)/index.tsx
import { useConversationStore } from '../../stores/useConversationStore';
import { requestMicrophonePermission } from '../../services/audio.service';

export default function ConversationScreen() {
  const { isConnected, startConversation, endConversation } = useConversationStore();

  const handlePress = async () => {
    if (isConnected) {
      await endConversation();
    } else {
      const hasPermission = await requestMicrophonePermission();
      if (hasPermission) {
        await startConversation();
      } else {
        Alert.alert('Microphone Required', 'Please enable microphone access in settings');
      }
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.status}>
        {isConnected ? 'Connected - Speak now' : 'Tap to start conversation'}
      </Text>

      <TouchableOpacity
        style={[styles.micButton, isConnected && styles.micButtonActive]}
        onPress={handlePress}
      >
        <MicrophoneIcon active={isConnected} />
      </TouchableOpacity>
    </View>
  );
}
```

**Wiring Up:**
```typescript
// File: mobile/src/app/(tabs)/index.tsx
// This is the HOME screen (main conversation screen)
// Already wired through tabs layout from Story 2.9
// No additional routing needed
```

**Prerequisites:** Stories 3.5 and 3.6 complete

---

### Story 3.8: Daily.co React Native Integration

**As a** frontend developer,
**I want** Daily.co client integrated in React Native,
**So that** the app can join voice rooms.

**Acceptance Criteria:**
1. Install `@daily-co/react-native-daily-js` package
2. Configure for Expo (may need custom development build)
3. Daily call object creation and joining working
4. Audio input/output working on device
5. Can hear bot speaking
6. Bot can hear user speaking
7. Connection status events handled
8. Participant events tracked
9. Works on Android (web already works via browser Daily.co)

**Technical Notes:**
```bash
# Install Daily.co React Native SDK
npm install @daily-co/react-native-daily-js
```

Note: May require Expo custom development build (not Expo Go) for native audio handling.

Alternative for MVP: Use web-only (PWA) first, add native later.

**Wiring Up:**
```typescript
// Import Daily.co in conversation store:
import DailyIframe from '@daily-co/react-native-daily-js';

// Already integrated in Story 3.5 - no additional wiring
// The store creates call object and manages connection
```

**Prerequisites:** Story 3.5 complete

---

### Story 3.9: End Conversation & Cleanup

**As a** user,
**I want** to end conversations cleanly,
**So that** resources are released and conversation is saved.

**Acceptance Criteria:**
1. Endpoint: `POST /api/v1/conversations/{id}/end` (requires auth)
2. Updates conversation record: `ended_at`, `duration_seconds`
3. Stops Pipecat bot process
4. Deletes Daily.co room
5. Frontend calls this when user ends conversation
6. Frontend cleans up Daily call object
7. Proper error handling if already ended
8. Can test multiple start/end cycles

**Technical Notes:**
```python
@router.post("/{conversation_id}/end")
async def end_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    conversation = session.get(Conversation, conversation_id)
    if not conversation or conversation.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if conversation.ended_at:
        raise HTTPException(status_code=400, detail="Conversation already ended")

    # Update conversation
    conversation.ended_at = datetime.utcnow()
    conversation.duration_seconds = int((conversation.ended_at - conversation.started_at).total_seconds())
    session.commit()

    # Clean up Daily room
    await delete_room(conversation.daily_room_id)

    return {"message": "Conversation ended", "duration_seconds": conversation.duration_seconds}
```

**Wiring Up:**
```python
# Add to conversations router (same file as /start endpoint)
# Route: POST /api/v1/conversations/{conversation_id}/end

# Frontend calls this automatically when user ends conversation
# Bot process should detect room closure and shut down gracefully
```

**Prerequisites:** Stories 3.4 and 3.7 complete

---

### Story 3.10: End-to-End Voice Test

**As a** developer,
**I want** to validate the complete voice pipeline,
**So that** I know voice conversations work end-to-end.

**Acceptance Criteria:**
1. Can start conversation from mobile app
2. Microphone permission granted
3. App joins Daily.co room successfully
4. User speaks: "Hello"
5. Speech detected by Deepgram (backend logs show transcription)
6. GPT-5-mini generates response (backend logs show LLM output)
7. ElevenLabs synthesizes speech (backend logs show TTS generation)
8. User hears AI voice response in app
9. Round-trip latency <5 seconds (aim for <3s in Epic 6)
10. Can end conversation cleanly

**Technical Notes:**
- Test with real devices (not just simulator)
- Check backend logs for pipeline events
- Monitor Daily.co dashboard for room activity
- Verify all API keys are working

**Manual Test Checklist:**
- [ ] Login to app
- [ ] Tap "Start Conversation"
- [ ] Grant microphone permission
- [ ] Wait for connection
- [ ] Say "Hello, can you hear me?"
- [ ] Hear AI response within 5 seconds
- [ ] Tap to end conversation
- [ ] Verify conversation saved in backend

**Prerequisites:** All previous stories in Epic 3 complete

---

## Epic 3 Summary

**What's Working After Epic 3:**
- ✅ Backend: Pipecat-ai bot with full voice pipeline
- ✅ Integration: Deepgram STT, GPT-5-mini LLM, ElevenLabs TTS
- ✅ Infrastructure: Daily.co rooms for WebRTC
- ✅ Frontend: Conversation screen with mic button
- ✅ State: Conversation state management
- ✅ Audio: Microphone permissions and Daily.co integration
- ✅ End-to-end: User can speak and hear AI respond

**Demo:**
1. Login to app
2. Tap "Start Conversation" button
3. Say "Hello" into microphone
4. Hear AI voice respond warmly
5. Have basic back-and-forth conversation
6. End conversation cleanly

**Limitations (to address in future epics):**
- No numerology knowledge yet (just basic greeting)
- No conversation history display
- No voice visualization
- No transcription display
- Basic error handling only

**Next Epic:** Numerology Engine Integration

---

## Epic 4: Numerology Engine Integration

**Goal:** Enable AI to calculate numerology numbers and provide expert interpretations during conversations

**Business Value:** Core product value - AI becomes an actual numerologist, not just a chatbot

**Testable Outcome:** User asks "What's my life path number?" → AI calculates from birth date → explains meaning with deep numerology knowledge

**Prerequisites:** Epic 3 complete (voice conversations working)

**Estimated Effort:** 2-3 days

---

### Story 4.1: Numerology Calculation Functions

**As a** backend developer,
**I want** Python functions for all numerology calculations,
**So that** the AI can compute numbers from user data.

**Acceptance Criteria:**
1. Service created in `backend/src/services/numerology_service.py`
2. `calculate_life_path(birth_date: date) -> int` - Returns 1-9, 11, 22, or 33
3. `calculate_expression_number(full_name: str) -> int` - Pythagorean system
4. `calculate_soul_urge(full_name: str) -> int` - Based on vowels
5. `calculate_birthday_number(birth_date: date) -> int` - Day of month
6. `calculate_personal_year(birth_date: date) -> int` - Current year cycle
7. All calculations follow Pythagorean numerology rules
8. Unit tests for each function with known test cases
9. `uv run pytest tests/test_numerology_service.py` passes

**Technical Notes:**
```python
# backend/src/services/numerology_service.py
from datetime import date

MASTER_NUMBERS = {11, 22, 33}

def calculate_life_path(birth_date: date) -> int:
    """Calculate Life Path number using reduction method"""
    # Reduce month, day, year separately, then combine
    month = _reduce_to_single(birth_date.month)
    day = _reduce_to_single(birth_date.day)
    year = _reduce_to_single(birth_date.year)

    total = month + day + year
    return _reduce_to_single(total)

def _reduce_to_single(number: int) -> int:
    """Reduce number to single digit or master number"""
    while number > 9 and number not in MASTER_NUMBERS:
        number = sum(int(digit) for digit in str(number))
    return number

# Similar pattern for other calculations...
```

**Wiring Up:**
```python
# Import in function calling handlers:
from src.services.numerology_service import (
    calculate_life_path,
    calculate_expression_number,
    calculate_soul_urge,
    calculate_birthday_number,
    calculate_personal_year
)

# Use when AI needs to calculate:
life_path = calculate_life_path(user.birth_date)
```

**Prerequisites:** Story 1.2 complete (backend setup)

---

### Story 4.2: Numerology Knowledge Base Schema & Seeding

**As a** backend developer,
**I want** a database table with numerology interpretations,
**So that** the AI can provide accurate, detailed guidance.

**Acceptance Criteria:**
1. `NumerologyInterpretation` model created in `backend/src/models/numerology_interpretation.py`
2. Fields: `id`, `number_type` (life_path/expression/etc), `number_value` (1-9, 11, 22, 33), `category` (personality/strengths/challenges), `content` (interpretation text)
3. Alembic migration creates table
4. Seed script created: `backend/src/scripts/seed_numerology.py`
5. Script populates comprehensive interpretations for all numbers
6. Can run: `uv run python -m src.scripts.seed_numerology`
7. Database contains 200+ interpretation entries covering all aspects

**Wiring Up:**
```python
# Import in services:
from src.models.numerology_interpretation import NumerologyInterpretation
from sqlmodel import select

# Query interpretations:
async def get_interpretation(number_type: str, value: int) -> List[str]:
    query = select(NumerologyInterpretation).where(
        NumerologyInterpretation.number_type == number_type,
        NumerologyInterpretation.number_value == value
    )
    results = await session.exec(query).all()
    return [r.content for r in results]
```

**Prerequisites:** Story 2.1 complete (database models pattern established)

---

### Story 4.3: GPT Function Calling Definitions

**As a** backend developer,
**I want** GPT function definitions for numerology tools,
**So that** the AI can call calculation functions during conversation.

**Acceptance Criteria:**
1. Function definitions file: `backend/src/voice_pipeline/numerology_functions.py`
2. Define tool for `calculate_life_path` with parameters
3. Define tool for `calculate_expression_number` with parameters
4. Define tool for `get_numerology_interpretation` with parameters
5. Each tool has clear description for GPT to understand when to use
6. Parameter schemas match calculation functions
7. Function definitions use OpenAI's tool format

**Technical Notes:**
```python
# backend/src/voice_pipeline/numerology_functions.py
NUMEROLOGY_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculate_life_path",
            "description": "Calculate the user's Life Path number from their birth date. This reveals their life purpose and journey.",
            "parameters": {
                "type": "object",
                "properties": {
                    "birth_date": {
                        "type": "string",
                        "format": "date",
                        "description": "User's birth date in YYYY-MM-DD format"
                    }
                },
                "required": ["birth_date"]
            }
        }
    },
    # ... more tools
]
```

**Wiring Up:**
```python
# In pipecat_bot.py, add tools to LLM context:
from src.voice_pipeline.numerology_functions import NUMEROLOGY_TOOLS

llm = AzureOpenAILLMService(...)
context = OpenAILLMContext(
    messages=[...],
    tools=NUMEROLOGY_TOOLS
)
```

**Prerequisites:** Story 3.3 complete (Pipecat bot created)

---

### Story 4.4: Function Call Handler Implementation

**As a** backend developer,
**I want** handlers that execute when GPT calls numerology functions,
**So that** calculations happen and results return to the AI.

**Acceptance Criteria:**
1. Handler file: `backend/src/voice_pipeline/function_handlers.py`
2. `handle_calculate_life_path(birth_date: str) -> dict` function
3. `handle_calculate_expression(full_name: str) -> dict` function
4. `handle_get_interpretation(number_type: str, value: int) -> dict` function
5. Handlers call numerology service functions
6. Handlers return results in format GPT expects
7. Error handling for invalid inputs
8. Logged execution for debugging

**Wiring Up:**
```python
# In pipecat_bot.py, register handlers:
from src.voice_pipeline.function_handlers import handle_numerology_function

@llm.event_handler("on_function_call")
async def on_function_call(function_name: str, arguments: dict):
    result = await handle_numerology_function(function_name, arguments)
    return result

# Handler routes to specific calculation:
async def handle_numerology_function(name: str, args: dict):
    if name == "calculate_life_path":
        return await handle_calculate_life_path(args["birth_date"])
    elif name == "calculate_expression_number":
        return await handle_calculate_expression(args["full_name"])
    # ... etc
```

**Prerequisites:** Stories 4.1, 4.2, 4.3 complete

---

### Story 4.5: Numerology System Prompt

**As a** backend developer,
**I want** a specialized system prompt that makes the AI a numerology expert,
**So that** conversations feel authentic and knowledgeable.

**Acceptance Criteria:**
1. System prompt file: `backend/src/voice_pipeline/system_prompts.py`
2. `get_numerology_system_prompt(user: User) -> str` function
3. Prompt includes: role (master numerologist), personality (wise, warm), knowledge scope
4. Prompt includes user context (name, birth date if available)
5. Prompt instructs AI to use function calls for calculations
6. Prompt sets conversational tone and boundaries
7. Prompt prevents AI from giving medical/financial advice

**Technical Notes:**
```python
def get_numerology_system_prompt(user: User) -> str:
    return f"""You are a master Pythagorean numerologist with deep knowledge of numerology.

Your name is Aria, and you're warm, wise, and genuinely interested in helping {user.full_name} understand their numerology.

KNOWLEDGE:
- You have comprehensive knowledge of Pythagorean numerology
- Life Path, Expression, Soul Urge, Birthday, and Personal Year numbers
- Master Numbers (11, 22, 33) and their special significance

TOOLS:
- Use calculate_life_path when you need the user's Life Path number
- Use calculate_expression_number for their Expression/Destiny number
- Use get_numerology_interpretation to access detailed interpretations

CONVERSATION STYLE:
- Speak naturally and conversationally
- Ask follow-up questions to understand their life situation
- Connect numerology insights to their specific questions
- Be encouraging and positive while acknowledging challenges

BOUNDARIES:
- This is for entertainment and spiritual guidance
- Don't give medical, legal, or financial advice
- If asked about serious issues, encourage seeking professional help

USER INFO:
- Name: {user.full_name}
- Birth Date: {user.birth_date.strftime('%B %d, %Y')}

Begin by warmly greeting {user.full_name} and asking how you can help them today."""
```

**Wiring Up:**
```python
# In pipecat_bot.py, use when creating bot:
from src.voice_pipeline.system_prompts import get_numerology_system_prompt
from src.models.user import User

async def run_bot(room_url: str, token: str, user: User):
    system_prompt = get_numerology_system_prompt(user)
    messages = [{"role": "system", "content": system_prompt}]
    # ... rest of pipeline setup
```

**Prerequisites:** Story 4.4 complete

---

### Story 4.6: Update Conversation Endpoint with User Context

**As a** backend developer,
**I want** the bot to receive user context when starting,
**So that** the AI knows the user's name and birth date.

**Acceptance Criteria:**
1. Update `start_conversation` endpoint to pass `User` object to bot
2. Bot initialization includes user context
3. System prompt generated with user data
4. AI can access user's birth date without asking
5. First message greets user by name

**Wiring Up:**
```python
# Update in conversations.py endpoint:
@router.post("/start")
async def start_conversation(current_user: User = Depends(get_current_user)):
    # ... create room ...

    # Pass user to bot
    asyncio.create_task(run_bot(room_data["room_url"], room_data["token"], current_user))
```

**Prerequisites:** Story 4.5 complete

---

### Story 4.7: Test Numerology Conversation End-to-End

**As a** developer,
**I want** to validate numerology calculations work in conversation,
**So that** I know the AI can actually be a numerologist.

**Acceptance Criteria:**
1. Start conversation from app
2. Ask: "What's my life path number?"
3. AI uses function call to calculate from user's birth date
4. AI receives result and explains meaning
5. Ask follow-up: "What does that mean for my career?"
6. AI provides career insights for that life path number
7. Conversation feels natural and knowledgeable
8. Backend logs show function calls executing
9. Calculations are mathematically correct
10. Can test with different users/birth dates

**Manual Test Script:**
```
User: "Hi, what's my life path number?"
Expected: AI calculates, then says something like:
"Your Life Path number is 7. This means you're a natural seeker of truth and wisdom..."

User: "What does that mean for relationships?"
Expected: AI provides relationship insights for Life Path 7

User: "Can you calculate my expression number?"
Expected: AI uses full name from profile, calculates, explains
```

**Prerequisites:** All previous stories in Epic 4 complete

---

## Epic 4 Summary

**What's Working After Epic 4:**
- ✅ Backend: All numerology calculation functions
- ✅ Database: Knowledge base with interpretations
- ✅ AI Integration: GPT function calling for calculations
- ✅ System Prompt: AI persona as expert numerologist
- ✅ End-to-end: User asks → AI calculates → AI explains with expertise

**Demo:**
1. Start conversation
2. Ask "What's my life path number?"
3. AI calculates from your birth date
4. AI explains meaning in detail
5. Ask follow-up questions about career, relationships
6. AI provides personalized numerology guidance

**Next Epic:** Conversation History & Context Retention

---

## Epic 5: Conversation History & Context Retention

**Goal:** Save conversation history and enable AI to remember past conversations

**Business Value:** Builds relationship with users - AI remembers their journey

**Testable Outcome:** User ends conversation → Can view history → Starts new conversation → AI references previous discussion

**Prerequisites:** Epic 4 complete (numerology working)

**Estimated Effort:** 2 days

---

### Story 5.1: Conversation Message Model & Saving

**As a** backend developer,
**I want** to save conversation messages during the session,
**So that** we have a record of what was discussed.

**Acceptance Criteria:**
1. `ConversationMessage` model created in `backend/src/models/conversation_message.py`
2. Fields: `id`, `conversation_id`, `role` (user/assistant), `content`, `timestamp`, `metadata` (JSON)
3. Alembic migration creates table
4. During conversation, each message saved to database
5. Messages linked to Conversation via foreign key
6. Can query messages for a conversation ordered by timestamp

**Wiring Up:**
```python
# In pipecat_bot.py, save messages as they occur:
from src.models.conversation_message import ConversationMessage

# Hook into message events:
@transport.event_handler("on_user_message")
async def save_user_message(message: str):
    msg = ConversationMessage(
        conversation_id=conversation_id,
        role="user",
        content=message,
        timestamp=datetime.utcnow()
    )
    session.add(msg)
    session.commit()

@transport.event_handler("on_assistant_message")
async def save_assistant_message(message: str):
    # Similar to above, role="assistant"
```

**Prerequisites:** Story 3.4 complete (Conversation model exists)

---

### Story 5.2: Get Conversation History Endpoint

**As a** user,
**I want** to view my past conversations,
**So that** I can see what we discussed before.

**Acceptance Criteria:**
1. Endpoint: `GET /api/v1/conversations` (requires auth)
2. Returns list of user's conversations with summary
3. Each conversation shows: id, started_at, ended_at, duration, main_topic
4. Paginated (20 per page)
5. Ordered by most recent first
6. Endpoint: `GET /api/v1/conversations/{id}` returns full conversation with all messages
7. Can test with Postman - see conversation list

**Wiring Up:**
```python
# Already added to conversations router in Story 3.4
# Just add GET endpoints to same router

@router.get("/", response_model=List[ConversationResponse])
async def list_conversations(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
    page: int = 1,
    limit: int = 20
):
    offset = (page - 1) * limit
    conversations = session.exec(
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .order_by(Conversation.started_at.desc())
        .offset(offset)
        .limit(limit)
    ).all()
    return conversations
```

**Prerequisites:** Story 5.1 complete

---

### Story 5.3: Frontend History Screen UI

**As a** user,
**I want** a history screen showing past conversations,
**So that** I can review what we talked about.

**Acceptance Criteria:**
1. History screen at `mobile/src/app/(tabs)/history.tsx`
2. Shows list of past conversations
3. Each item displays: date, duration, brief summary/topic
4. Tap to view full conversation details
5. Pull-to-refresh to reload list
6. Loading state while fetching
7. Empty state if no conversations yet
8. Pagination (load more on scroll)

**Wiring Up:**
```typescript
// File: mobile/src/app/(tabs)/history.tsx
// Already wired through tabs layout from Story 2.9
// Just implement the UI and call the API

import { apiClient } from '@/services/api';

const fetchHistory = async () => {
  const response = await apiClient.get('/api/v1/conversations');
  return response.data;
};
```

**Prerequisites:** Story 5.2 complete

---

### Story 5.4: Conversation Detail View

**As a** user,
**I want** to see the full transcript of a past conversation,
**So that** I can review what the AI told me.

**Acceptance Criteria:**
1. Detail screen at `mobile/src/app/conversation/[id].tsx`
2. Shows conversation metadata (date, duration)
3. Displays full message history (user & AI messages)
4. Messages formatted as chat bubbles
5. User messages on right, AI messages on left
6. Scrollable if long conversation
7. Can navigate back to history list

**Wiring Up:**
```typescript
// File: mobile/src/app/conversation/[id].tsx
// Expo Router dynamic route automatically handles [id] parameter

import { useLocalSearchParams } from 'expo-router';

export default function ConversationDetailScreen() {
  const { id } = useLocalSearchParams();

  // Fetch conversation details
  const response = await apiClient.get(`/api/v1/conversations/${id}`);
}
```

**Prerequisites:** Story 5.3 complete

---

### Story 5.5: Load Conversation Context for AI

**As a** backend developer,
**I want** the AI to load previous conversation summaries when starting,
**So that** it can reference past discussions.

**Acceptance Criteria:**
1. When bot starts, load recent 5 conversations for user
2. Create summary of each past conversation
3. Include summaries in system prompt context
4. AI can reference "As we discussed last time..."
5. Context doesn't exceed token limits (summarize if needed)
6. Cached in Redis for fast access

**Wiring Up:**
```python
# In pipecat_bot.py, load context before starting:
async def run_bot(room_url: str, token: str, user: User):
    # Get recent conversations
    recent_convos = await get_recent_conversations(user.id, limit=5)

    # Add to system prompt
    context_summary = format_conversation_history(recent_convos)
    system_prompt = get_numerology_system_prompt(user, context_summary)

    messages = [{"role": "system", "content": system_prompt}]
    # ... rest of pipeline
```

**Prerequisites:** Stories 5.1 and 5.2 complete

---

### Story 5.6: Test Context Retention End-to-End

**As a** developer,
**I want** to verify the AI remembers past conversations,
**So that** I know context retention works.

**Acceptance Criteria:**
1. Start first conversation, ask about Life Path number
2. End conversation
3. View conversation in history
4. Start second conversation
5. AI greets and references previous discussion
6. Ask "What did we talk about last time?"
7. AI accurately recalls previous topic
8. Conversation history shows both sessions

**Manual Test Script:**
```
Session 1:
User: "What's my life path number?"
AI: "Your Life Path is 7..." [explains]
User: [ends conversation]

Session 2:
AI: "Welcome back! Last time we explored your Life Path 7..."
User: "What did you tell me about relationships?"
AI: "As we discussed, Life Path 7 in relationships..." [recalls]
```

**Prerequisites:** All previous stories in Epic 5 complete

---

### Story 5.7: User Observations Database Schema

**As a** backend developer,
**I want** a database table to store AI-observed user patterns,
**So that** we can track user concerns for better personalization.

**Acceptance Criteria:**
1. `UserObservation` model created in `backend/src/models/user_observation.py`
2. Fields: `id`, `user_id`, `conversation_id`, `observation_type` (intent/wish/struggle/issue/goal), `content`, `confidence` (0.0-1.0), `extracted_at`, `metadata` (JSON)
3. Foreign keys to User and Conversation tables
4. Indexes on (user_id, observation_type) and conversation_id
5. Alembic migration created and applied
6. Model relationships updated in User and Conversation models
7. Can query observations by user and type

**Technical Notes:**
```python
# backend/src/models/user_observation.py
class UserObservation(SQLModel, table=True):
    __tablename__ = "user_observation"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    conversation_id: UUID = Field(foreign_key="conversation.id", index=True)
    observation_type: str = Field(index=True)  # "intent", "wish", "struggle", "issue", "goal"
    content: str = Field(sa_column=Column(Text))
    confidence: float = Field(default=0.0)
    extracted_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict = Field(default_factory=dict, sa_column=Column(JSON))
```

**Prerequisites:** Story 5.1 complete (Conversation model exists)

---

### Story 5.8: Observation Extraction Service

**As a** backend developer,
**I want** a service that extracts user observations from conversations,
**So that** we can automatically identify user patterns.

**Acceptance Criteria:**
1. `ObservationService` created in `backend/src/services/observation_service.py`
2. `extract_observations()` method uses GPT to identify patterns from conversation
3. Extracts: intents, wishes, struggles, issues, goals with confidence scores
4. Runs asynchronously during conversation (non-blocking)
5. Saves observations to database
6. Handles extraction errors gracefully
7. Unit tests for service methods
8. Extraction accuracy >80% on test conversations

**Technical Notes:**
```python
# backend/src/services/observation_service.py
class ObservationService:
    async def extract_observations(
        self,
        conversation_id: str,
        user_id: str,
        user_message: str,
        assistant_response: str
    ) -> List[UserObservation]:
        # Call GPT for extraction
        prompt = self._build_extraction_prompt(user_message, assistant_response)
        observations = await self._call_gpt_for_extraction(prompt)

        # Save to database
        return await self._save_observations(observations, conversation_id, user_id)
```

**Wiring Up:**
```python
# In pipecat_bot.py, add async extraction:
asyncio.create_task(
    observation_service.extract_observations(
        conversation_id, user_id, user_message, assistant_response
    )
)
```

**Prerequisites:** Story 5.7 complete (database schema exists)

---

### Story 5.9: Observations API Endpoints

**As a** user,
**I want** to access my observed patterns via API,
**So that** I can understand my tracked concerns.

**Acceptance Criteria:**
1. Router created in `backend/src/api/v1/endpoints/observations.py`
2. `GET /api/v1/observations` - List user's observations (paginated)
3. Query parameters: `type` (filter by type), `limit` (default 20)
4. `GET /api/v1/observations/summary` - Aggregated insights
5. Returns observations with type, content, confidence, date
6. Requires authentication
7. Response schemas in `backend/src/schemas/observation.py`
8. API documentation updated

**Technical Notes:**
```python
@router.get("/observations", response_model=List[ObservationResponse])
async def get_user_observations(
    observation_type: Optional[str] = None,
    limit: int = Query(default=20, le=100),
    current_user: User = Depends(get_current_user),
    observation_service: ObservationService = Depends()
):
    return await observation_service.get_user_observations(
        user_id=current_user.id,
        observation_type=observation_type,
        limit=limit
    )
```

**Prerequisites:** Story 5.8 complete (service exists)

---

### Story 5.10: GPT Observation Extraction Prompts

**As a** backend developer,
**I want** optimized prompts for extracting observations,
**So that** we get accurate pattern identification.

**Acceptance Criteria:**
1. Extraction prompts created in `backend/src/voice_pipeline/observation_prompts.py`
2. Prompt instructs GPT to identify user patterns from conversation
3. Returns structured JSON with type, content, confidence
4. Handles multiple observations per exchange
5. Filters out low-confidence (<0.5) observations
6. Prompts tested for accuracy and consistency
7. System prompt updated to prime observation awareness
8. 80%+ accuracy in categorizing observation types

**Technical Notes:**
```python
EXTRACTION_PROMPT = """
Analyze this conversation exchange and identify user patterns:

User: {user_message}
Assistant: {assistant_response}

Extract any:
- INTENT: What the user is trying to achieve
- WISH: What they hope for
- STRUGGLE: Challenges they face
- ISSUE: Specific problems mentioned
- GOAL: What they want to accomplish

Return as JSON:
[
  {"type": "intent|wish|struggle|issue|goal", "content": "...", "confidence": 0.0-1.0},
  ...
]
"""
```

**Prerequisites:** Story 5.8 complete (extraction service needs prompts)

---

### Story 5.11: Integration with Voice Pipeline

**As a** backend developer,
**I want** observation extraction integrated into the voice pipeline,
**So that** observations are captured during natural conversation.

**Acceptance Criteria:**
1. Pipecat bot modified to trigger observation extraction
2. Extraction runs after each meaningful exchange
3. Non-blocking async processing (doesn't affect latency)
4. Handles extraction failures without disrupting conversation
5. Logs extraction events for monitoring
6. Voice latency remains <3 seconds
7. End-to-end test: conversation → observations saved

**Wiring Up:**
```python
# In pipecat_bot.py:
@transport.event_handler("on_exchange_complete")
async def handle_exchange(user_msg: str, assistant_msg: str):
    # Fire and forget - don't await
    asyncio.create_task(
        observation_service.extract_observations(
            conversation_id=self.conversation_id,
            user_id=self.user_id,
            user_message=user_msg,
            assistant_response=assistant_msg
        )
    )
```

**Prerequisites:** Stories 5.8 and 5.10 complete

---

### Story 5.12: Test Observations End-to-End

**As a** developer,
**I want** to validate the complete observations pipeline,
**So that** I know user patterns are being tracked correctly.

**Acceptance Criteria:**
1. Have conversation expressing various concerns
2. Check database for extracted observations
3. Call API to retrieve observations
4. Verify observation types are correctly categorized
5. Confidence scores are reasonable (>0.5)
6. No impact on voice conversation latency
7. Observations appear within 5 seconds of exchange

**Manual Test Script:**
```
Conversation:
User: "I wish I could understand my career path better"
→ Observation: type="wish", content="understand career path better"

User: "I'm struggling with making decisions"
→ Observation: type="struggle", content="making decisions"

User: "My goal is to find my life purpose"
→ Observation: type="goal", content="find life purpose"

Verify via API:
GET /api/v1/observations
→ Returns all extracted observations
```

**Prerequisites:** All previous stories in Epic 5 complete

---

## Epic 5 Summary

**What's Working After Epic 5:**
- ✅ Backend: Conversation messages saved to database
- ✅ API: Endpoints to list and view conversations
- ✅ Frontend: History screen with conversation list
- ✅ Detail View: Full conversation transcripts
- ✅ Context: AI remembers and references past conversations
- ✅ Observations: AI extracts and stores user patterns (intents, wishes, struggles, issues, goals)
- ✅ Insights API: Endpoints to retrieve user observations for personalization
- ✅ Non-blocking: Observation extraction doesn't impact voice latency

**Demo:**
1. Have conversation expressing concerns and goals
2. AI extracts observations (wishes, struggles, goals) in background
3. Go to History tab → See conversation listed
4. Call API → See extracted observations with confidence scores
5. Start new conversation → AI references previous discussion
6. Over time → AI understands user patterns for deeper personalization

**Next Epic:** Voice UX Polish & Visual Feedback

---

## Epic 6: Voice UX Polish & Visual Feedback

**Goal:** Add visual polish and feedback to make voice conversations feel alive

**Business Value:** Professional, delightful user experience - the "wow" factor

**Testable Outcome:** Voice visualizer animates with speech → Transcription displays live → Beautiful animations throughout

**Prerequisites:** Epic 5 complete (core features done)

**Estimated Effort:** 2-3 days

---

### Story 6.1: Voice Amplitude Visualization Component

**As a** user,
**I want** to see visual feedback when speaking,
**So that** I know the app is listening.

**Acceptance Criteria:**
1. Component created: `mobile/src/components/conversation/VoiceVisualizer.tsx`
2. Animated wave forms that respond to audio amplitude
3. Different animation when user speaking vs AI speaking
4. Smooth 60fps animations
5. Uses React Native Animated API
6. Customizable colors (user: blue, AI: purple)
7. Works on both web and mobile

**Wiring Up:**
```typescript
// In ConversationScreen:
import { VoiceVisualizer } from '@/components/conversation/VoiceVisualizer';

<VoiceVisualizer
  isActive={isConnected}
  isUserSpeaking={isMicActive}
  isAISpeaking={isAISpeaking}
/>

// Connect to Daily.co audio events:
dailyCall.on('participant-speaking', (event) => {
  if (event.participant.local) {
    setIsMicActive(true);
  } else {
    setIsAISpeaking(true);
  }
});
```

**Prerequisites:** Story 3.7 complete (conversation screen exists)

---

### Story 6.2: Live Transcription Display

**As a** user,
**I want** to see what I'm saying transcribed in real-time,
**So that** I can confirm the AI heard me correctly.

**Acceptance Criteria:**
1. Component: `mobile/src/components/conversation/TranscriptionDisplay.tsx`
2. Shows user's speech as text appears
3. Shows AI's response text as it's spoken
4. Different styling for user vs AI text
5. Auto-scrolls as text appears
6. Fades out after 10 seconds (doesn't clutter screen)
7. Optional toggle to hide transcriptions

**Wiring Up:**
```typescript
// Connect to Daily.co transcription events or Pipecat events
// Store transcription in conversation store

const useConversationStore = create((set) => ({
  currentTranscription: '',
  updateTranscription: (text) => set({ currentTranscription: text }),
}));

// In ConversationScreen:
<TranscriptionDisplay text={currentTranscription} role="user" />
```

**Prerequisites:** Story 6.1 complete

---

### Story 6.3: Numerology Number Display Cards

**As a** user,
**I want** to see my numerology numbers displayed beautifully,
**So that** they feel special and memorable.

**Acceptance Criteria:**
1. Component: `mobile/src/components/conversation/NumberDisplay.tsx`
2. Large, elegant display of calculated numbers
3. Animated reveal when number is calculated
4. Shows number + brief meaning
5. Beautiful card design (gradient background, shadows)
6. Tappable to see full interpretation
7. Can display multiple numbers (Life Path, Expression, etc.)

**Wiring Up:**
```typescript
// When AI calculates a number, store it and display:
const useConversationStore = create((set) => ({
  calculatedNumbers: [],
  addNumber: (number) => set((state) => ({
    calculatedNumbers: [...state.calculatedNumbers, number]
  })),
}));

// Listen to function call results from backend
// When calculate_life_path returns, add to store
// Component displays from store
```

**Prerequisites:** Epic 4 complete (numerology calculations working)

---

### Story 6.4: Loading States & Animations

**As a** user,
**I want** smooth loading animations,
**So that** the app feels responsive and polished.

**Acceptance Criteria:**
1. Loading spinner when connecting to conversation
2. Skeleton loading for history list
3. Shimmer effect for loading conversation details
4. Smooth transitions between screens
5. Fade in/out animations
6. Button press feedback (haptics on mobile)
7. No jarring loading states

**Wiring Up:**
```typescript
// Use throughout app:
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';

{isLoading ? <LoadingSpinner /> : <Content />}

// Add to stores for loading states:
const useAuthStore = create((set) => ({
  isLoading: false,
  // ... set isLoading true before API calls, false after
}));
```

**Prerequisites:** All previous UI stories complete

---

### Story 6.5: Error Handling & User Feedback

**As a** user,
**I want** clear error messages when something goes wrong,
**So that** I know what to do to fix it.

**Acceptance Criteria:**
1. Error component: `mobile/src/components/ui/ErrorMessage.tsx`
2. User-friendly error messages (not technical jargon)
3. Actionable guidance ("Check your internet connection")
4. Retry button for transient errors
5. Different styles for warning vs error
6. Toast notifications for quick feedback
7. Graceful degradation (app doesn't crash)

**Wiring Up:**
```typescript
// Use throughout app:
import { ErrorMessage } from '@/components/ui/ErrorMessage';
import { Toast } from '@/components/ui/Toast';

// In stores, catch errors and show:
try {
  await apiCall();
} catch (error) {
  Toast.show({
    type: 'error',
    message: getErrorMessage(error),
    action: { label: 'Retry', onPress: handleRetry }
  });
}
```

**Prerequisites:** Epic 3 complete (error scenarios exist)

---

### Story 6.6: Settings Screen with Voice Preferences

**As a** user,
**I want** to adjust voice settings,
**So that** I can customize my experience.

**Acceptance Criteria:**
1. Settings screen: `mobile/src/app/(tabs)/settings.tsx`
2. Voice speed slider (0.8x - 1.2x)
3. Voice volume control
4. Transcription on/off toggle
5. Notification preferences
6. Settings persisted locally
7. Applied in next conversation

**Wiring Up:**
```typescript
// Store in AsyncStorage:
import AsyncStorage from '@react-native-async-storage/async-storage';

const saveSettings = async (settings) => {
  await AsyncStorage.setItem('voiceSettings', JSON.stringify(settings));
};

// Load and apply when starting conversation:
const settings = await AsyncStorage.getItem('voiceSettings');
// Send to backend or apply client-side
```

**Prerequisites:** Epic 2 complete (tabs navigation exists)

---

## Epic 6 Summary

**What's Working After Epic 6:**
- ✅ Visual Feedback: Voice visualizer, transcriptions
- ✅ Beautiful UI: Number display cards, animations
- ✅ Polish: Loading states, error handling, smooth transitions
- ✅ Customization: Settings screen with preferences

**Demo:**
1. Start conversation → See voice visualizer animate
2. Speak → See live transcription appear
3. AI calculates number → Beautiful card reveals with animation
4. Navigate screens → Smooth transitions
5. Adjust settings → Voice speed changes

**Next Epic:** Data Privacy & Security

---

## Epic 7: Data Privacy & Security

**Goal:** Implement production-grade security and privacy controls

**Business Value:** User trust, GDPR compliance, secure data handling

**Testable Outcome:** All data encrypted → Rate limiting works → User can export/delete data

**Prerequisites:** Epic 6 complete (all features done)

**Estimated Effort:** 2 days

---

### Story 7.1: API Rate Limiting with Redis

**As a** backend developer,
**I want** rate limiting on all endpoints,
**So that** we prevent abuse and manage costs.

**Acceptance Criteria:**
1. Rate limiting middleware in `backend/src/middleware/rate_limit.py`
2. Uses Redis to track request counts
3. Different limits per endpoint type:
   - Auth endpoints: 5/minute
   - Conversation start: 10/hour
   - General API: 60/hour
4. Returns 429 Too Many Requests with retry-after header
5. Rate limits per user (authenticated) or IP (anonymous)
6. Configurable limits via environment variables

**Wiring Up:**
```python
# In backend/src/main.py:
from src.middleware.rate_limit import rate_limit_middleware

app.add_middleware(rate_limit_middleware)

# Or per-route:
from src.middleware.rate_limit import rate_limit

@router.post("/start")
@rate_limit(max_requests=10, window_seconds=3600)
async def start_conversation():
    pass
```

**Prerequisites:** Story 1.4 complete (Redis available)

---

### Story 7.2: Data Export (GDPR Compliance)

**As a** user,
**I want** to export all my data,
**So that** I can see what information is stored.

**Acceptance Criteria:**
1. Endpoint: `GET /api/v1/users/me/export` (requires auth)
2. Returns JSON with all user data:
   - Profile information
   - All conversations with messages
   - Calculated numerology numbers
   - Account metadata
3. Generates export file asynchronously if large
4. Email download link when ready
5. Export link expires after 24 hours

**Wiring Up:**
```python
@router.get("/me/export")
async def export_user_data(current_user: User = Depends(get_current_user)):
    # Gather all user data
    data = {
        "profile": {...},
        "conversations": [...],
        "numerology": {...},
        "account": {...}
    }
    return data
```

**Prerequisites:** All data models complete

---

### Story 7.3: Account Deletion (Right to be Forgotten)

**As a** user,
**I want** to delete my account and all data,
**So that** I can exercise my privacy rights.

**Acceptance Criteria:**
1. Endpoint: `DELETE /api/v1/users/me` (requires auth)
2. Soft delete initially (marks account as deleted)
3. Scheduled job for permanent deletion after 30 days
4. Deletes: user, conversations, messages, numerology data
5. Cannot be undone (shows confirmation)
6. User logged out immediately
7. All API tokens invalidated

**Wiring Up:**
```python
@router.delete("/me")
async def delete_account(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Soft delete
    current_user.is_active = False
    current_user.deleted_at = datetime.utcnow()
    session.commit()

    # Invalidate tokens
    await redis.delete(f"user:tokens:{current_user.id}")

    return {"message": "Account scheduled for deletion"}
```

**Prerequisites:** Epic 2 complete (user management exists)

---

### Story 7.4: Environment Variable Security

**As a** developer,
**I want** secure handling of API keys and secrets,
**So that** credentials aren't exposed.

**Acceptance Criteria:**
1. `.env.example` documents all required variables
2. `.env` in `.gitignore` (never committed)
3. All secrets loaded from environment
4. Validation on startup (fails if required vars missing)
5. Different configs for dev/staging/prod
6. Secrets rotation process documented
7. No secrets in logs or error messages

**Wiring Up:**
```python
# backend/src/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    JWT_SECRET: str
    DATABASE_URL: str
    REDIS_URL: str
    DAILY_API_KEY: str
    DEEPGRAM_API_KEY: str
    AZURE_OPENAI_API_KEY: str
    ELEVENLABS_API_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()

# Validates on import - crashes if missing
```

**Prerequisites:** Story 1.2 complete (backend setup)

---

### Story 7.5: HTTPS & Security Headers

**As a** backend developer,
**I want** proper security headers and HTTPS enforcement,
**So that** communications are secure.

**Acceptance Criteria:**
1. HTTPS enforced in production (redirect HTTP → HTTPS)
2. Security headers middleware:
   - X-Content-Type-Options: nosniff
   - X-Frame-Options: DENY
   - X-XSS-Protection: 1; mode=block
   - Strict-Transport-Security (HSTS)
3. CORS properly configured (only allow frontend domain)
4. Content Security Policy (CSP) headers
5. No sensitive data in URLs (use POST body)

**Wiring Up:**
```python
# In backend/src/main.py:
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

if settings.ENVIRONMENT == "production":
    app.add_middleware(HTTPSRedirectMiddleware)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["numerologist-ai.com"])

# Security headers
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    # ... more headers
    return response
```

**Prerequisites:** Epic 1 complete (backend running)

---

### Story 7.6: Audit Logging for Sensitive Operations

**As a** developer,
**I want** audit logs for sensitive operations,
**So that** we can track security-relevant events.

**Acceptance Criteria:**
1. Log: user registration, login, logout
2. Log: account deletion requests
3. Log: data export requests
4. Log: failed authentication attempts
5. Logs include: timestamp, user_id, IP, action, outcome
6. Stored in database and/or log aggregation service
7. Regular review process for security team

**Wiring Up:**
```python
# backend/src/services/audit_service.py
async def log_audit_event(
    user_id: UUID,
    action: str,
    outcome: str,
    metadata: dict
):
    event = AuditLog(
        user_id=user_id,
        action=action,
        outcome=outcome,
        metadata=metadata,
        timestamp=datetime.utcnow()
    )
    session.add(event)
    session.commit()

# Use throughout:
await log_audit_event(user.id, "LOGIN", "SUCCESS", {"ip": request.client.host})
```

**Prerequisites:** Story 2.1 complete (database setup)

---

## Epic 7 Summary

**What's Working After Epic 7:**
- ✅ Security: Rate limiting, HTTPS, security headers
- ✅ Privacy: Data export, account deletion, GDPR compliance
- ✅ Audit: Logging of sensitive operations
- ✅ Secrets: Secure environment variable handling

**Demo:**
1. Try rapid API requests → Rate limited
2. Request data export → Receive JSON with all data
3. Delete account → Account marked for deletion
4. All communications over HTTPS with security headers

**Next Epic:** Performance Optimization & Deployment

---

## Epic 8: Performance Optimization & Deployment

**Goal:** Optimize performance and deploy to production (Azure)

**Business Value:** Fast, scalable app ready for users

**Testable Outcome:** Voice latency <3s → App loads <3s → Deployed to production URL

**Prerequisites:** Epic 7 complete (all features and security done)

**Estimated Effort:** 2-3 days

---

### Story 8.1: Redis Caching Layer

**As a** backend developer,
**I want** Redis caching for expensive operations,
**So that** API responses are fast.

**Acceptance Criteria:**
1. Cache numerology interpretations (24 hour TTL)
2. Cache user profiles (1 hour TTL)
3. Cache conversation context (30 day TTL)
4. Cache wrapper utility for easy reuse
5. Cache invalidation on data updates
6. Monitor cache hit rates

**Wiring Up:**
```python
# backend/src/core/cache.py
from functools import wraps

def cached(ttl: int):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{args}:{kwargs}"
            cached_value = await redis.get(cache_key)
            if cached_value:
                return json.loads(cached_value)

            result = await func(*args, **kwargs)
            await redis.set(cache_key, json.dumps(result), ex=ttl)
            return result
        return wrapper
    return decorator

# Use:
@cached(ttl=86400)  # 24 hours
async def get_interpretation(number_type: str, value: int):
    return await db.query(...)
```

**Prerequisites:** Story 1.4 complete (Redis available)

---

### Story 8.2: Database Query Optimization

**As a** backend developer,
**I want** optimized database queries,
**So that** API responses are fast.

**Acceptance Criteria:**
1. Review all queries for N+1 problems
2. Add eager loading where needed (SQLModel `selectinload`)
3. Database indexes on foreign keys
4. Indexes on frequently queried fields
5. Query explain plans for slow queries
6. Pagination for large result sets
7. Query execution time <100ms

**Wiring Up:**
```python
# Use selectinload to avoid N+1:
from sqlmodel import selectinload

query = (
    select(Conversation)
    .options(selectinload(Conversation.messages))
    .where(Conversation.user_id == user_id)
)

# Add indexes in migrations:
# CREATE INDEX idx_conversation_user_started ON conversation(user_id, started_at DESC);
```

**Prerequisites:** All models complete

---

### Story 8.3: Voice Pipeline Latency Optimization

**As a** backend developer,
**I want** optimized voice pipeline for <3s latency,
**So that** conversations feel natural.

**Acceptance Criteria:**
1. Measure current end-to-end latency
2. Optimize Pipecat pipeline configuration
3. Use streaming TTS (don't wait for full generation)
4. Pre-warm connections to APIs
5. Use VAD (Voice Activity Detection) to reduce silence
6. Monitor latency per component
7. Achieve <3s average, <5s 95th percentile

**Wiring Up:**
```python
# In pipecat_bot.py, enable optimizations:
transport = DailyTransport(
    room_url,
    token,
    "Bot",
    DailyParams(
        audio_in_enabled=True,
        audio_out_enabled=True,
        vad_enabled=True,  # Voice Activity Detection
        vad_analyzer=SileroVADAnalyzer(
            params=SileroVADParams(
                min_volume=0.6,  # Tune for sensitivity
            )
        )
    )
)

# Use streaming TTS:
tts = ElevenLabsTTSService(
    api_key=settings.ELEVENLABS_API_KEY,
    voice_id="...",
    model="eleven_turbo_v2",  # Faster model
    streaming=True
)
```

**Prerequisites:** Epic 3 complete (voice pipeline exists)

---

### Story 8.4: Frontend Bundle Optimization

**As a** frontend developer,
**I want** optimized bundle size and loading,
**So that** the app loads quickly.

**Acceptance Criteria:**
1. Bundle size <50MB for mobile app
2. Web bundle <2MB (gzipped)
3. Code splitting for routes
4. Lazy load heavy components
5. Image optimization (WebP, proper sizing)
6. Remove unused dependencies
7. App launch time <3s

**Wiring Up:**
```typescript
// Use React.lazy for code splitting:
const HistoryScreen = React.lazy(() => import('@/app/(tabs)/history'));

// In app.json, enable Hermes:
{
  "expo": {
    "jsEngine": "hermes",
    "android": {
      "enableProguardInReleaseBuilds": true,
      "enableShrinkResourcesInReleaseBuilds": true
    }
  }
}

// Analyze bundle:
npx expo-cli build:web --analyze
```

**Prerequisites:** Epic 1 complete (frontend exists)

---

### Story 8.5: Backend Deployment to Azure

**As a** DevOps engineer,
**I want** backend deployed to Azure,
**So that** it's accessible from the internet.

**Acceptance Criteria:**
1. Azure Container Apps for FastAPI backend
2. Azure Database for PostgreSQL (managed)
3. Azure Cache for Redis (managed)
4. Environment variables configured in Azure
5. HTTPS with custom domain
6. Health checks configured
7. Auto-scaling: 2-10 instances
8. Deployment via GitHub Actions CI/CD

**Wiring Up:**
```yaml
# .github/workflows/deploy-backend.yml
name: Deploy Backend

on:
  push:
    branches: [main]
    paths: ['backend/**']

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build and push Docker
        run: |
          docker build -t numerologist-api:${{ github.sha }} ./backend
          docker push ${{ secrets.ACR_NAME }}.azurecr.io/numerologist-api:${{ github.sha }}

      - name: Deploy to Azure Container Apps
        run: |
          az containerapp update \
            --name numerologist-api \
            --image ${{ secrets.ACR_NAME }}.azurecr.io/numerologist-api:${{ github.sha }}
```

**Prerequisites:** Epic 7 complete (security configured)

---

### Story 8.6: Frontend Deployment (PWA + Android)

**As a** DevOps engineer,
**I want** frontend deployed for users to access,
**So that** people can use the app.

**Acceptance Criteria:**
1. PWA deployed to Azure Static Web Apps
2. Android APK built via Expo EAS
3. Android app submitted to Google Play Store (internal testing)
4. Custom domain configured (numerologist-ai.com)
5. SSL certificate active
6. PWA installable on mobile browsers
7. Deep linking works for both web and native

**Wiring Up:**
```bash
# Build PWA:
cd mobile
npm run build:web
az storage blob upload-batch -s ./web-build -d $web-container

# Build Android:
eas build --platform android --profile production

# Submit to Play Store:
eas submit --platform android --latest
```

**Prerequisites:** Epic 1 complete (frontend exists)

---

### Story 8.7: Monitoring & Alerting Setup

**As a** DevOps engineer,
**I want** monitoring and alerts,
**So that** I know when something breaks.

**Acceptance Criteria:**
1. Azure Application Insights for backend
2. Log aggregation and searchable logs
3. Alerts for:
   - API error rate >5%
   - Voice latency >5s
   - Database connection failures
   - High memory/CPU usage
4. Dashboard with key metrics
5. On-call rotation for critical alerts
6. Weekly report of metrics

**Wiring Up:**
```python
# In backend/src/main.py:
from opencensus.ext.azure.log_exporter import AzureLogHandler

logger.addHandler(AzureLogHandler(
    connection_string=settings.APPINSIGHTS_CONNECTION_STRING
))

# Track custom metrics:
from applicationinsights import TelemetryClient
tc = TelemetryClient(settings.APPINSIGHTS_KEY)

# Track voice latency:
tc.track_metric('voice_latency', latency_ms)
```

**Prerequisites:** Story 8.5 complete (deployed to Azure)

---

### Story 8.8: Production Testing & Launch Checklist

**As a** product owner,
**I want** comprehensive testing before launch,
**So that** users have a great experience.

**Acceptance Criteria:**
1. End-to-end testing on production environment
2. Load testing (100 concurrent users)
3. Security audit passed
4. Privacy policy published
5. Terms of service published
6. Support email configured
7. Analytics tracking active
8. Backup and disaster recovery tested
9. Rollback plan documented
10. Launch announcement prepared

**Manual Production Test:**
```
✓ Register new account
✓ Login successfully
✓ Start voice conversation
✓ Ask numerology questions
✓ AI responds with calculations
✓ View conversation history
✓ Export data (GDPR)
✓ Adjust settings
✓ Logout and login again
✓ Delete account
✓ All data removed
```

**Prerequisites:** All previous stories in Epic 8 complete

---

## Epic 8 Summary

**What's Working After Epic 8:**
- ✅ Performance: Redis caching, optimized queries, <3s voice latency
- ✅ Deployment: Backend on Azure, PWA live, Android on Play Store
- ✅ Monitoring: Application Insights, alerts, dashboards
- ✅ Production Ready: Tested, secured, monitored

**Demo:**
1. Visit https://numerologist-ai.com
2. Register account
3. Start conversation - responds in <3s
4. Install PWA to home screen
5. Download Android app from Play Store
6. Everything works smoothly in production!

---

## Implementation Sequence & Dependency Graph

### Phase 1: Foundation (Week 1)
**Goal:** Development environment working

**Stories (can run in parallel):**
- Story 1.1: Monorepo structure
- Story 1.2: Backend with uv ✱
- Story 1.3: Frontend with Expo ✱
- Story 1.4: Docker Compose ✱

**Sequential after parallel:**
- Story 1.5: Database connection (requires 1.2, 1.4)
- Story 1.6: API client (requires 1.3, 1.5)
- Story 1.7: Makefile (requires all above)

**Checkpoint:** `make dev` starts everything, app shows "API Status: Connected"

---

### Phase 2: User System (Week 2)
**Goal:** Users can register and login

**Backend (sequential):**
- Story 2.1: User model → 2.2: Security utils → 2.3: Register endpoint → 2.4: Login endpoint → 2.5: Get user endpoint

**Frontend (after 2.2):**
- Story 2.6: Auth store (requires API client)
- Story 2.7: Login screen ✱ (parallel with 2.8)
- Story 2.8: Register screen ✱ (parallel with 2.7)
- Story 2.9: Profile screen (requires 2.7, 2.8)
- Story 2.10: Auth navigation (requires 2.9)

**Checkpoint:** Register → Login → See profile → Logout

---

### Phase 3: Voice Pipeline (Week 3)
**Goal:** Voice conversations working

**Backend (sequential):**
- Story 3.1: Voice dependencies
- Story 3.2: Daily.co service (requires 3.1)
- Story 3.3: Pipecat bot (requires 3.2)
- Story 3.4: Conversation endpoints (requires 3.3)

**Frontend (after 3.1):**
- Story 3.5: Conversation store (requires API client) ✱
- Story 3.6: Microphone permissions ✱
- Story 3.7: Conversation screen (requires 3.5, 3.6)
- Story 3.8: Daily.co integration (requires 3.7)
- Story 3.9: End conversation (requires 3.4, 3.8)

**Testing:**
- Story 3.10: End-to-end voice test (requires all above)

**Checkpoint:** Speak into app → Hear AI respond

---

### Phase 4: Numerology Intelligence (Week 4)
**Goal:** AI becomes a numerologist

**Backend (mostly parallel):**
- Story 4.1: Calculation functions ✱
- Story 4.2: Knowledge base seeding ✱
- Story 4.3: Function definitions (requires 4.1) ✱
- Story 4.4: Function handlers (requires 4.1, 4.2, 4.3)
- Story 4.5: System prompt (requires 4.4)
- Story 4.6: Update bot with context (requires 4.5)

**Testing:**
- Story 4.7: Test numerology conversation (requires all above)

**Checkpoint:** Ask "What's my life path?" → AI calculates and explains

---

### Phase 5: History & Memory (Week 5)
**Goal:** Conversations saved and AI remembers

**Backend:**
- Story 5.1: Message model (requires Conversation model)
- Story 5.2: History endpoints (requires 5.1)

**Frontend:**
- Story 5.3: History screen (requires 5.2) ✱
- Story 5.4: Detail view (requires 5.3) ✱

**Context:**
- Story 5.5: Load context for AI (requires 5.1, 5.2)
- Story 5.6: Test context retention (requires all)

**Checkpoint:** View history → Start new chat → AI remembers

---

### Phase 6: Polish (Week 6)
**Goal:** Beautiful, professional UX

**Frontend (mostly parallel):**
- Story 6.1: Voice visualizer ✱
- Story 6.2: Transcription display ✱
- Story 6.3: Number cards ✱
- Story 6.4: Loading states ✱
- Story 6.5: Error handling ✱
- Story 6.6: Settings screen ✱

**Checkpoint:** Professional UI with animations and feedback

---

### Phase 7: Security & Privacy (Week 7)
**Goal:** Production-grade security

**Backend (can run in parallel):**
- Story 7.1: Rate limiting ✱
- Story 7.2: Data export ✱
- Story 7.3: Account deletion ✱
- Story 7.4: Environment security ✱
- Story 7.5: HTTPS & headers ✱
- Story 7.6: Audit logging ✱

**Checkpoint:** Rate limiting works, GDPR compliance tested

---

### Phase 8: Deployment & Launch (Week 8)
**Goal:** Live in production

**Performance (parallel):**
- Story 8.1: Redis caching ✱
- Story 8.2: Query optimization ✱
- Story 8.3: Voice latency optimization ✱
- Story 8.4: Bundle optimization ✱

**Deployment (sequential):**
- Story 8.5: Backend to Azure
- Story 8.6: Frontend deployment (requires 8.5)
- Story 8.7: Monitoring setup (requires 8.5, 8.6)
- Story 8.8: Production testing (requires all)

**Checkpoint:** App live at https://numerologist-ai.com

---

## Development Statistics

**Total Stories:** 58 stories across 8 epics

**Parallel Opportunities:**
- Phase 1: 3 stories can run in parallel
- Phase 2: 2 stories in parallel
- Phase 3: 2 stories in parallel
- Phase 4: 3 stories in parallel
- Phase 5: 2 stories in parallel
- Phase 6: 6 stories in parallel
- Phase 7: 6 stories in parallel
- Phase 8: 4 stories in parallel

**Sequential Chains:**
- Longest chain: ~15 stories (foundation → auth → voice → numerology)
- Average story size: 200-300 lines of code per story
- Estimated effort: 8 weeks with 1-2 developers

**Story Complexity Distribution:**
- Simple (1-2 hours): 20 stories (setup, config, simple UI)
- Medium (2-4 hours): 30 stories (API endpoints, components, integrations)
- Complex (4-8 hours): 8 stories (Pipecat bot, complex state, optimization)

---

## Story Validation Summary

All 58 stories validated against these criteria:

**Size Check:** ✅
- Every story <500 words description
- Clear inputs and outputs
- Single responsibility
- No hidden complexity

**Clarity Check:** ✅
- Explicit acceptance criteria (avg 7-10 criteria per story)
- Clear technical approach with code examples
- No ambiguous requirements
- Measurable success

**Dependency Check:** ✅
- Dependencies explicitly documented
- Clear starting inputs
- Well-defined outputs
- Parallel opportunities marked with ✱

**Testability Check:** ✅
- Each story has testable outcome
- Acceptance criteria are verifiable
- Manual test steps provided where needed
- Can demo after completion

**Vertical Slice Check:** ✅
- Stories deliver end-to-end value
- Frontend + backend together within each epic
- No orphaned backend-only work
- Everything is immediately testable

**AI Agent Compatibility:** ✅
- Each story fits in 200k context window
- Wiring notes show how to integrate
- Can complete independently
- Clear success criteria

---

## Implementation Guidance for Development Teams

### Getting Started - First Day

**Day 1 - Quick Wins:**
1. Start with Story 1.1 (monorepo structure) - 30 minutes
2. Run Stories 1.2, 1.3, 1.4 in parallel (3 agents or developers) - 2 hours
3. Then Story 1.5, 1.6 sequentially - 1 hour
4. End day with Story 1.7 - **you have `make dev` working!**

**Week 1 Goal:**
- Complete Epic 1 (Foundation) - Days 1-2
- Complete Epic 2 (Auth) - Days 3-5
- Start Epic 3 (Voice) - Day 5

### Development Workflow

**For each story:**
```bash
# 1. Read story acceptance criteria
# 2. Read wiring notes
# 3. Reference architecture.md for patterns
# 4. Implement code
# 5. Test acceptance criteria
# 6. Commit with story ID: "Story 2.3: User registration endpoint"
# 7. Mark story complete
```

**Agent allocation (for AI agents):**
- Give agent: Story description + Architecture doc + Wiring notes
- Agent completes story in one session
- No need to see entire codebase
- Context stays under 200k tokens

**Human developers:**
- Backend dev: Focus on Stories X.1-X.4 each epic
- Frontend dev: Focus on Stories X.5-X.10 each epic
- Sync at epic boundaries to integration test

### Critical Technical Decisions to Make Early

**Before Epic 1:**
- ✅ Already decided: uv for Python, Expo for mobile, simple monorepo

**During Epic 3 (Voice):**
- Decision needed: Web-only PWA first vs native Android first?
  - Recommendation: Web PWA first (simpler), Android in Epic 6
  - Native audio needs custom dev build, PWA works immediately

**During Epic 4 (Numerology):**
- Decision needed: How comprehensive should knowledge base be?
  - Recommendation: Start with basics (100 interpretations), expand later
  - Can update database without code deployment

### Technology-Specific Guidance

**uv (Backend Package Management):**
```bash
# Starting a story that needs new package:
cd backend
uv add <package-name>
uv sync

# Running backend during development:
uv run uvicorn src.main:app --reload

# Running tests:
uv run pytest
uv run pytest tests/test_specific.py -v

# Code formatting:
uv run black src/
uv run ruff check src/
```

**Expo (Frontend Development):**
```bash
# Starting dev server:
cd mobile
npm start

# Running on different platforms:
# Press 'w' → web browser
# Press 'a' → Android emulator (needs Android Studio)
# Scan QR → physical device with Expo Go

# Building for production:
eas build --platform web
eas build --platform android --profile production

# Note: First time needs 'eas login' and 'eas build:configure'
```

**Pipecat-ai (Voice Pipeline):**
- Study examples: https://github.com/pipecat-ai/pipecat/tree/main/examples
- Key concept: Pipeline is list of processors
- Order matters: Input → STT → LLM → TTS → Output
- Use aggregators for context management
- Monitor logs during development - very verbose but helpful

**Daily.co (WebRTC):**
- Dashboard: https://dashboard.daily.co
- Check "Logs" tab during testing
- Room URL pattern: `https://{domain}.daily.co/{room-name}`
- Free tier: 1000 minutes/month (enough for development)

### Testing Strategy per Epic

**Epic 1:** Manual - run commands, verify output
**Epic 2:** API tests + manual UI testing
**Epic 3:** End-to-end manual (Story 3.10), backend unit tests
**Epic 4:** Unit tests for calculations, manual conversation tests
**Epic 5:** Manual testing with multiple sessions
**Epic 6:** Visual QA, manual interaction testing
**Epic 7:** Security audit, penetration testing
**Epic 8:** Load testing, production smoke tests

### Common Pitfalls & Solutions

**Pitfall: Import errors between backend modules**
- Solution: Always import from `src.*`, never relative imports
- Example: `from src.models.user import User` (not `from models.user`)

**Pitfall: Expo Router not finding routes**
- Solution: Ensure `src/app/` structure is correct
- Check app.json for proper configuration
- Clear Metro cache: `npm start -- --clear`

**Pitfall: Database migrations out of sync**
- Solution: Always run `alembic upgrade head` after pulling changes
- Don't edit migration files manually
- Use `alembic revision --autogenerate` for new changes

**Pitfall: Pipecat bot not connecting to Daily room**
- Solution: Check all 4 API keys are valid (Daily, Deepgram, OpenAI, ElevenLabs)
- Check Daily room exists (check dashboard)
- Check bot logs for connection errors

**Pitfall: Voice latency too high**
- Solution: Don't worry in Epic 3, optimize in Epic 8
- Check internet connection during testing
- Ensure using streaming TTS (not batch)

### Risk Mitigation Strategies

**Risk: Voice latency >3s (NFR-P1 requirement)**
- **Mitigation:** Epic 8.3 dedicated to optimization
- **Fallback:** Can accept <5s for MVP, optimize post-launch
- **Monitoring:** Track from Epic 3 onward, identify bottlenecks early

**Risk: Pipecat-ai complexity overwhelming**
- **Mitigation:** Start simple (Story 3.3 basic greeting), add features incrementally
- **Fallback:** Pipecat has active Discord community, GitHub discussions
- **Testing:** Story 3.10 validates core pipeline before building more

**Risk: Native mobile audio not working**
- **Mitigation:** PWA works immediately without native builds
- **Fallback:** Launch web PWA first, add native Android in Phase 2
- **Note:** Story 3.8 flags this - may need Expo custom dev build for native

**Risk: API costs exceeding budget ($0.15/conversation target)**
- **Mitigation:** Epic 7.1 rate limiting controls usage
- **Monitoring:** Epic 8.7 tracks costs per conversation
- **Fallback:** Reduce conversation length limits if needed

**Risk: Numerology knowledge accuracy questioned**
- **Mitigation:** Story 4.2 seeds from verified numerology sources
- **Validation:** Have numerology expert review AI responses
- **Fallback:** Can update database interpretations without code deployment

### Success Metrics per Epic

| Epic | Success Metric | How to Validate |
|------|---------------|-----------------|
| **Epic 1** | `make dev` works first time | Run command, both services start |
| **Epic 2** | Can create account and login | Complete registration flow |
| **Epic 3** | Can have voice conversation | Speak and hear AI respond |
| **Epic 4** | AI demonstrates numerology expertise | Ask numerology questions, validate answers |
| **Epic 5** | AI remembers past conversations | Start 2nd conversation, AI references 1st |
| **Epic 6** | UI feels polished and professional | Show to non-technical user, get feedback |
| **Epic 7** | Security audit passes | Run security checklist, no critical issues |
| **Epic 8** | App live and performing well | Voice latency <3s, app loads <3s |

---

## Next Steps for Hieu

### Immediate Actions

1. **Review this epic breakdown**
   - Does the story organization make sense?
   - Are there any missing features you want in MVP?
   - Any stories that should be split or combined?

2. **Run Solutioning Gate Check** ✅ (Already in progress!)
   - Validates alignment between PRD, Architecture, and these Epics
   - Identifies any gaps or contradictions
   - Ensures implementation readiness

3. **Create Sprint Plan**
   - Once gate check passes, organize stories into sprints
   - Run: `/bmad:bmm:workflows:sprint-planning`

4. **Begin Implementation**
   - Start with Epic 1, Story 1.1
   - Use: `/bmad:bmm:workflows:dev-story` for guided implementation

### Development Approach Options

**Option A: Sequential Solo Development (8 weeks)**
- Work through epics 1-8 in order
- Test thoroughly after each epic
- Advantages: Full context, consistent quality
- Disadvantages: Slower, no parallelization

**Option B: Two-Track Parallel (6 weeks)**
- Developer A: Backend stories (X.1-X.4)
- Developer B: Frontend stories (X.5-X.10)
- Sync and integrate at epic boundaries
- Advantages: Faster, specialized focus
- Disadvantages: Requires coordination

**Option C: AI Agent Swarm (4 weeks)**
- Multiple AI agents work in parallel
- Each agent takes one story at a time
- Human reviews and integrates
- Advantages: Very fast, handles tedious work
- Disadvantages: Requires oversight, integration work

**Recommendation for Hieu:** Option B or C - leverage parallelization

---

## Reference: All Epics at a Glance

| Epic | Stories | Focus | Estimated Effort |
|------|---------|-------|------------------|
| **1. Foundation** | 7 | Monorepo setup, dev environment | 1-2 days |
| **2. Auth** | 10 | User registration, login, profile | 2-3 days |
| **3. Voice** | 10 | Pipecat pipeline, real-time conversations | 3-4 days |
| **4. Numerology** | 7 | Calculations, knowledge, function calling | 2-3 days |
| **5. History** | 6 | Conversation storage, context retention | 2 days |
| **6. Polish** | 6 | Visual feedback, animations, UX | 2-3 days |
| **7. Security** | 6 | Rate limiting, GDPR, encryption | 2 days |
| **8. Deployment** | 8 | Optimization, Azure, monitoring | 2-3 days |
| **TOTAL** | **58** | **Complete MVP** | **8 weeks** |

---

_Epic breakdown created using BMM methodology v6-alpha_
_Created: 2025-11-04_
_Total: 8 epics, 58 stories, ~8 weeks estimated effort_
_Every story is testable, every epic delivers value, every component has wiring notes_

**Ready for implementation!** 🚀

