# Architecture - Numerologist AI

## Executive Summary

Numerologist AI is a voice-first conversational AI platform built with a modern, scalable architecture optimized for real-time voice interactions. The system uses React Native (Expo) for cross-platform mobile delivery (Web PWA + Android) and FastAPI for a high-performance Python backend. The voice pipeline leverages Pipecat-ai to orchestrate Deepgram (STT), Azure OpenAI GPT-5-mini (LLM), and ElevenLabs (TTS) through Daily.co WebRTC infrastructure.

**Architectural Approach:** Client-server with real-time voice streaming, optimized for <3 second voice latency, supporting 100-1,000+ concurrent users with PostgreSQL + Redis caching.

**Key Design Principles:**
- Voice-first: All interactions optimized for natural conversation
- Simplicity: Leverage starters and managed services to reduce complexity
- Performance: Redis caching, async operations, optimized voice pipeline
- Scalability: Horizontal scaling ready, stateless services where possible

## Project Initialization

**First Implementation Story: Initialize Project Foundation**

The project uses two official starter templates that establish the base architecture:

### Frontend - React Native with Expo

```bash
npx create-expo-app@latest numerologist-ai --template blank-typescript
cd numerologist-ai
```

**Provided by Expo Starter:**
- TypeScript configuration
- React Native + Expo SDK (latest)
- Metro bundler with hot reload
- Cross-platform support (Web, iOS, Android)
- Native module access (audio, microphone, permissions)
- Build tools for PWA and native apps

### Backend - FastAPI + Pipecat-ai

```bash
# Create FastAPI project
pipx run copier copy https://github.com/fastapi/full-stack-fastapi-template numerologist-ai-backend --trust
cd numerologist-ai-backend/backend

# Add voice pipeline dependencies
pip install "pipecat-ai[daily,deepgram,openai,cartesia]"
pip install redis redis[hiredis]
pip install elevenlabs
pip install deepgram-sdk
```

**Provided by FastAPI Starter:**
- FastAPI with automatic OpenAPI docs
- PostgreSQL database + SQLModel ORM
- Alembic for database migrations
- JWT authentication infrastructure
- Docker Compose for development
- Pytest testing setup
- CORS and security configurations

**Added for Voice Pipeline:**
- Pipecat-ai framework for voice orchestration
- Deepgram SDK (v5.2.0) for STT
- Azure OpenAI integration for GPT-5-mini
- ElevenLabs SDK (v2.17.0) for TTS
- Daily.co integration via Pipecat
- Redis for caching and session management

---

## Decision Summary

| Category | Decision | Version | Affects Epics | Rationale |
| -------- | -------- | ------- | ------------- | --------- |
| **Voice Services** |
| Speech-to-Text | Deepgram | SDK v5.2.0 (Oct 2025) | Voice Pipeline | Industry-leading accuracy, low latency (<800ms), noise suppression |
| LLM Reasoning | Azure OpenAI GPT-5-mini | Aug 2025 | All epics | Real-time optimized, function calling for numerology, cost-effective |
| Text-to-Speech | ElevenLabs | SDK v2.17.0 (Oct 2025) | Voice Pipeline | Natural conversational voice, low latency (<700ms) |
| WebRTC Transport | Daily.co | Via Pipecat integration | Voice Pipeline | Managed WebRTC, reliable mobile support, Pipecat-native |
| Voice Orchestration | Pipecat-ai | Latest (Python >=3.11) | Voice Pipeline | Framework handles LLM context, function calling, pipeline state |
| **Frontend Stack** |
| Framework | React Native + Expo | Latest | All frontend | Cross-platform (Web PWA + Android), official recommended approach |
| Language | TypeScript | Latest | All frontend | Type safety, better DX, catches errors early |
| State Management | Zustand | Latest | All frontend | Lightweight, simple API, perfect for voice state |
| API Client | Axios + React Query | Latest | All frontend | Automatic caching, request deduplication, background refetch |
| Styling | React Native StyleSheet | Built-in | All frontend | Native performance, TypeScript support |
| **Backend Stack** |
| Framework | FastAPI | Latest (Python 3.11+) | All backend | Async/await, auto docs, high performance |
| Database | PostgreSQL | 14+ | All epics | Robust, ACID compliant, excellent for relational data |
| ORM | SQLModel | Latest | All backend | FastAPI-native, Pydantic integration, type-safe queries |
| Caching | Redis | 7-alpine | All epics | Sub-millisecond access, session storage, rate limiting |
| Migrations | Alembic | Latest | All backend | Database version control, team collaboration |
| **Authentication** |
| Primary Auth | JWT Tokens | - | User Management | Stateless, scalable, industry standard |
| Token Lifetime | Access: 15min, Refresh: 7 days | - | User Management | Balance security and UX |
| OAuth Provider | Google OAuth | - | User Management | Android users prefer Google sign-in |
| Password Hashing | bcrypt | Cost factor: 12 | User Management | Industry standard, resistant to brute force |
| **Data & Caching** |
| Session Storage | Redis | - | Auth, Voice Pipeline | Fast lookup, automatic expiration |
| Numerology Cache | Redis + PostgreSQL | - | Numerology Engine | Redis for speed, PostgreSQL as source of truth |
| Conversation Context | Redis | TTL: 30 days | Voice Pipeline | Fast AI context loading |
| API Rate Limiting | Redis | - | All endpoints | Prevent abuse, manage costs |
| **Numerology Engine** |
| Calculations | Python functions | - | Numerology Engine | Pure logic, fast, deterministic |
| Knowledge Base | PostgreSQL | - | Numerology Engine | Flexible, updatable without deployment |
| Interpretation Cache | Redis | TTL: 24 hours | Numerology Engine | Fast retrieval, reduce DB load |
| **Deployment** |
| Hosting | Azure | - | All | OpenAI integration, managed Redis, scalable |
| Backend Deployment | Docker containers | - | Backend | Consistent environments, easy scaling |
| Frontend Deployment | Expo EAS + Web hosting | - | Frontend | PWA + Android native builds |
| Database Hosting | Azure PostgreSQL | - | Backend | Managed service, automatic backups |
| Cache Hosting | Azure Cache for Redis | - | Backend | Managed service, high availability |

---

## Project Structure

```
numerologist-ai/                          # Root monorepo
│
├── numerologist-ai/                      # Frontend (React Native + Expo)
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── login.tsx
│   │   │   ├── register.tsx
│   │   │   └── _layout.tsx
│   │   ├── (tabs)/
│   │   │   ├── index.tsx                # Home/Conversation screen
│   │   │   ├── history.tsx              # Past conversations
│   │   │   ├── profile.tsx              # User profile
│   │   │   └── _layout.tsx
│   │   └── _layout.tsx
│   ├── components/
│   │   ├── conversation/
│   │   │   ├── MicrophoneButton.tsx
│   │   │   ├── VoiceVisualizer.tsx
│   │   │   ├── TranscriptionDisplay.tsx
│   │   │   └── NumberDisplay.tsx
│   │   ├── ui/
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   └── Card.tsx
│   │   └── shared/
│   │       ├── ErrorBoundary.tsx
│   │       └── LoadingSpinner.tsx
│   ├── hooks/
│   │   ├── useConversation.ts
│   │   ├── useMicrophone.ts
│   │   ├── useAuth.ts
│   │   └── useNumerology.ts
│   ├── services/
│   │   ├── api.ts                       # Axios instance with interceptors
│   │   ├── auth.service.ts
│   │   ├── conversation.service.ts
│   │   └── numerology.service.ts
│   ├── stores/
│   │   ├── useAuthStore.ts              # Zustand: auth state
│   │   ├── useConversationStore.ts      # Zustand: voice state
│   │   └── useNumerologyStore.ts        # Zustand: numerology data
│   ├── types/
│   │   ├── user.types.ts
│   │   ├── conversation.types.ts
│   │   └── numerology.types.ts
│   ├── utils/
│   │   ├── voice.utils.ts
│   │   ├── date.utils.ts
│   │   └── storage.utils.ts
│   ├── constants/
│   │   ├── Colors.ts
│   │   └── Config.ts
│   ├── app.json
│   ├── package.json
│   └── tsconfig.json
│
└── numerologist-ai-backend/             # Backend (FastAPI + Pipecat)
    ├── backend/
    │   ├── app/
    │   │   ├── api/
    │   │   │   └── v1/
    │   │   │       ├── endpoints/
    │   │   │       │   ├── auth.py
    │   │   │       │   ├── users.py
    │   │   │       │   ├── conversations.py
    │   │   │       │   └── numerology.py
    │   │   │       └── router.py
    │   │   ├── core/
    │   │   │   ├── config.py
    │   │   │   ├── security.py
    │   │   │   ├── redis.py
    │   │   │   └── database.py
    │   │   ├── models/
    │   │   │   ├── user.py
    │   │   │   ├── conversation.py
    │   │   │   ├── numerology_profile.py
    │   │   │   └── numerology_interpretation.py
    │   │   ├── schemas/
    │   │   │   ├── user.py
    │   │   │   ├── conversation.py
    │   │   │   └── numerology.py
    │   │   ├── services/
    │   │   │   ├── numerology_service.py
    │   │   │   ├── voice_service.py
    │   │   │   └── daily_service.py
    │   │   ├── voice_pipeline/
    │   │   │   ├── pipecat_bot.py        # Main pipeline setup
    │   │   │   ├── voice_handlers.py     # Function call handlers
    │   │   │   └── system_prompts.py     # AI system prompts
    │   │   └── main.py
    │   ├── alembic/
    │   │   ├── versions/
    │   │   └── env.py
    │   ├── tests/
    │   │   ├── api/
    │   │   ├── services/
    │   │   └── conftest.py
    │   ├── requirements.txt
    │   └── Dockerfile
    ├── docker-compose.yml
    └── .env.example
```

---

## Epic to Architecture Mapping

Epic breakdown will be created in the next workflow phase, but here's the architectural mapping structure:

| Epic | Primary Components | Database Tables | APIs | External Services |
|------|-------------------|-----------------|------|-------------------|
| **Foundation & Infrastructure** | FastAPI app, Expo app, Docker setup | N/A | Health check | None |
| **User Management & Auth** | auth.py, users.py, useAuthStore | user | /api/v1/auth/*, /api/v1/users/* | Google OAuth |
| **Voice Pipeline Integration** | pipecat_bot.py, voice_service.py | N/A | /api/v1/conversations/start | Deepgram, OpenAI, ElevenLabs, Daily.co |
| **Numerology Engine** | numerology_service.py | numerology_profile, numerology_interpretation | /api/v1/numerology/* | None |
| **Conversation Management** | conversations.py, useConversationStore | conversation, conversation_message | /api/v1/conversations/* | Daily.co |
| **Mobile UI & Voice UX** | Conversation components, MicrophoneButton | N/A | N/A | None |
| **Data Privacy & Security** | security.py, encryption middleware | All tables | All endpoints | None |
| **Performance & Deployment** | Redis caching, Docker, monitoring | N/A | All endpoints | Azure services |

---

## Technology Stack Details

### Core Technologies

**Frontend:**
- **React Native 0.73+**: Cross-platform mobile framework
- **Expo SDK 50+**: Development tools, native modules, build service
- **TypeScript 5+**: Type-safe JavaScript
- **Zustand 4+**: Lightweight state management (1kb)
- **React Query 5+**: Server state management, caching
- **Axios**: HTTP client with interceptors
- **Expo SecureStore**: Encrypted token storage
- **date-fns**: Date/time utilities
- **Daily.co React Native SDK**: WebRTC client for voice

**Backend:**
- **FastAPI 0.109+**: Modern Python web framework
- **Python 3.10+**: Async/await, type hints, modern features
- **SQLModel**: Database ORM (Pydantic + SQLAlchemy)
- **PostgreSQL 14+**: Relational database
- **Redis 7+**: In-memory cache and session store
- **Alembic**: Database migrations
- **Pydantic**: Data validation
- **bcrypt**: Password hashing
- **python-jose**: JWT token handling

**Voice Pipeline:**
- **Pipecat-ai**: Voice conversation orchestration framework
- **Deepgram SDK 5.2.0**: Speech-to-text
- **Azure OpenAI GPT-5-mini**: LLM reasoning with function calling
- **ElevenLabs SDK 2.17.0**: Text-to-speech
- **Daily.co Python SDK**: WebRTC infrastructure

### Integration Points

**External Services:**

1. **Deepgram (Speech-to-Text)**
   - Endpoint: Streaming WebSocket via Pipecat
   - Authentication: API key
   - Latency target: <800ms
   - Error handling: Fallback to silence detection, retry on connection loss

2. **Azure OpenAI GPT-5-mini (LLM)**
   - Endpoint: Azure OpenAI API
   - Authentication: API key
   - Model: gpt-5-mini
   - Latency target: <1500ms
   - Features: Function calling for numerology tools
   - Error handling: Retry with exponential backoff (3 attempts)

3. **ElevenLabs (Text-to-Speech)**
   - Endpoint: Streaming API via Pipecat
   - Authentication: API key
   - Voice: Conversational voice (configurable)
   - Latency target: <700ms
   - Error handling: Fallback to default voice, retry on failure

4. **Daily.co (WebRTC Infrastructure)**
   - Endpoint: REST API for room management
   - Authentication: API key
   - Room TTL: 2 hours
   - Features: Real-time audio streaming, participant management
   - Error handling: Room creation retry, automatic cleanup on expiry

5. **Google OAuth (Authentication)**
   - Endpoint: Google OAuth 2.0
   - Flow: Authorization code flow
   - Scopes: email, profile
   - Error handling: Graceful fallback to email/password

**Service Communication Patterns:**

```
Frontend → Backend API (REST/JSON over HTTPS)
Backend → PostgreSQL (SQLModel ORM)
Backend → Redis (redis-py async client)
Backend → Daily.co (REST API)
Pipecat Bot → Daily.co (WebRTC)
Pipecat Bot → Deepgram (WebSocket)
Pipecat Bot → Azure OpenAI (REST API)
Pipecat Bot → ElevenLabs (Streaming API)
```

**Data Flow for Voice Conversation:**

```
1. User taps "Start Conversation"
2. Frontend → POST /api/v1/conversations/start
3. Backend creates Daily.co room + Conversation record
4. Backend spawns Pipecat bot process (joins Daily room)
5. Frontend joins Daily room with returned token
6. User speaks → Daily.co → Pipecat bot
7. Pipecat: Audio → Deepgram (STT) → Text
8. Pipecat: Text → OpenAI GPT-5-mini (with numerology functions)
9. If function call: Execute numerology_service functions
10. Pipecat: GPT response → ElevenLabs (TTS) → Audio
11. Pipecat: Audio → Daily.co → Frontend plays audio
12. Loop continues until user ends conversation
13. Frontend → POST /api/v1/conversations/{id}/end
14. Backend saves summary, closes Daily room, stops Pipecat bot
```

---

## Implementation Patterns

These patterns ensure consistent implementation across all AI agents:

### Voice Pipeline Patterns

**Pattern: Pipecat Bot Lifecycle**
```python
# All voice conversations follow this pattern
async def create_conversation_bot(conversation_id: str, user_id: str):
    # 1. Get user context
    user = await db.get_user(user_id)
    profile = await numerology_service.get_full_profile(user)

    # 2. Create Daily room
    room = await daily_service.create_room(conversation_id)

    # 3. Build system prompt with user context
    system_prompt = await build_system_prompt(user, profile)

    # 4. Initialize Pipecat services
    daily_transport = DailyTransport(room_url=room.url, token=room.token)
    stt = DeepgramSTTService(api_key=settings.DEEPGRAM_API_KEY)
    llm = OpenAILLMService(api_key=settings.AZURE_OPENAI_KEY, model="gpt-5-mini")
    tts = ElevenLabsTTSService(api_key=settings.ELEVENLABS_API_KEY)

    # 5. Set up LLM context with numerology functions
    context = OpenAILLMContext(messages=[{"role": "system", "content": system_prompt}])
    context.set_tools(get_numerology_functions())

    # 6. Create pipeline (Pipecat handles orchestration)
    pipeline = Pipeline([
        daily_transport.input(),
        stt,
        LLMUserResponseAggregator(context),
        llm,
        tts,
        daily_transport.output(),
        LLMAssistantResponseAggregator(context)
    ])

    # 7. Register function handlers
    @llm.event_handler("on_function_call")
    async def handle_function_call(function_name: str, arguments: dict):
        return await execute_numerology_function(function_name, arguments)

    # 8. Run pipeline
    await pipeline.run()
```

**Pattern: Numerology Function Calling**
```python
# GPT-5-mini can call these functions during conversation
NUMEROLOGY_FUNCTIONS = [
    {
        "type": "function",
        "function": {
            "name": "calculate_life_path",
            "description": "Calculate user's Life Path number",
            "parameters": {
                "type": "object",
                "properties": {
                    "birth_date": {"type": "string", "format": "date"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_numerology_interpretation",
            "description": "Get detailed interpretation for a numerology number",
            "parameters": {
                "type": "object",
                "properties": {
                    "number_type": {"type": "string", "enum": ["life_path", "expression", "soul_urge", "birthday"]},
                    "value": {"type": "integer"}
                },
                "required": ["number_type", "value"]
            }
        }
    }
]
```

### Caching Patterns

**Pattern: Check Cache → Compute → Store**
```python
# All expensive operations follow this pattern
async def get_cached_data(cache_key: str, compute_fn: Callable, ttl: int):
    # 1. Check Redis
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)

    # 2. Compute if miss
    data = await compute_fn()

    # 3. Store in Redis + PostgreSQL
    await redis.set(cache_key, json.dumps(data), ex=ttl)
    await db.save(data)

    return data

# Usage
profile = await get_cached_data(
    f"numerology:{user_id}:profile",
    lambda: numerology_service.calculate_full_profile(user),
    ttl=31536000  # 1 year
)
```

### API Response Patterns

**Pattern: Consistent Response Wrapper**
```python
# All API endpoints return this structure
class APIResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[ErrorDetail] = None
    message: Optional[str] = None

class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[dict] = None
    retry: bool = False

# Success example
@router.get("/users/me")
async def get_current_user(current_user: User = Depends(get_current_user)):
    return APIResponse(success=True, data=current_user)

# Error example
@app.exception_handler(ValueError)
async def validation_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=422,
        content=APIResponse(
            success=False,
            error=ErrorDetail(
                code="VALIDATION_ERROR",
                message=str(exc),
                retry=False
            )
        ).dict()
    )
```

### Frontend State Patterns

**Pattern: Zustand Store with Actions**
```typescript
// All stores follow this pattern
interface StoreState {
  // State
  data: T | null
  isLoading: boolean
  error: string | null

  // Actions
  fetch: () => Promise<void>
  update: (data: Partial<T>) => void
  reset: () => void
}

// Example: Conversation store
const useConversationStore = create<ConversationStore>((set, get) => ({
  // State
  conversationId: null,
  dailyCall: null,
  isConnected: false,
  isMicActive: false,
  isAISpeaking: false,
  error: null,

  // Actions
  startConversation: async () => {
    try {
      set({ isLoading: true, error: null })
      const response = await conversationService.start()

      // Join Daily room
      const call = await joinDailyRoom(response.data.daily_room_url, response.data.daily_token)

      set({
        conversationId: response.data.conversation_id,
        dailyCall: call,
        isConnected: true,
        isLoading: false
      })
    } catch (error) {
      set({ error: error.message, isLoading: false })
    }
  },

  endConversation: async () => {
    const { conversationId, dailyCall } = get()
    await conversationService.end(conversationId)
    await dailyCall?.leave()
    set({ conversationId: null, dailyCall: null, isConnected: false })
  },

  toggleMic: () => {
    const { dailyCall, isMicActive } = get()
    dailyCall?.setLocalAudio(!isMicActive)
    set({ isMicActive: !isMicActive })
  }
}))
```

---

## Consistency Rules

### Naming Conventions

**API Endpoints:**
- Format: `/api/v1/resource-name` (kebab-case)
- Collections: Plural (`/conversations`, `/users`)
- Single resource: `/{id}` parameter
- Actions: POST to collection or `/{id}/action`

**Examples:**
```
✅ POST   /api/v1/conversations/start
✅ GET    /api/v1/conversations
✅ GET    /api/v1/conversations/{id}
✅ POST   /api/v1/conversations/{id}/end
✅ POST   /api/v1/numerology/calculate
✅ DELETE /api/v1/users/me

❌ /api/v1/Conversation (wrong case)
❌ /api/v1/conversation (should be plural)
❌ /api/v1/conversations/{id}/endConversation (use verb not camelCase)
```

**Database Tables & Columns:**
- Tables: `snake_case`, singular
- Columns: `snake_case`
- Foreign keys: `{table}_id`
- Timestamps: `created_at`, `updated_at`
- Boolean: `is_active`, `has_profile`

**Examples:**
```sql
✅ CREATE TABLE user (id, email, full_name, birth_date, created_at)
✅ CREATE TABLE conversation (id, user_id, started_at, ended_at)
✅ CREATE TABLE numerology_profile (id, user_id, life_path_number)

❌ CREATE TABLE Users (wrong case)
❌ CREATE TABLE conversation (userId) (should be user_id)
❌ CREATE TABLE numerology_profile (lifePathNumber) (should be snake_case)
```

**Python Code:**
- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions: `snake_case()`
- Constants: `UPPER_SNAKE_CASE`
- Private: `_leading_underscore`

**Examples:**
```python
✅ # File: numerology_service.py
✅ class NumerologyService:
✅     MASTER_NUMBERS = [11, 22, 33]
✅
✅     def calculate_life_path(self, birth_date: date) -> int:
✅         return self._reduce_to_single_digit(sum_digits)
✅
✅     def _reduce_to_single_digit(self, number: int) -> int:
✅         pass

❌ class numerologyService (wrong case)
❌ def CalculateLifePath() (wrong case)
❌ masterNumbers = [11, 22, 33] (constants should be UPPER)
```

**TypeScript/React Native:**
- Files: Components = `PascalCase.tsx`, Others = `camelCase.ts`
- Components: `PascalCase`
- Hooks: `useCamelCase`
- Interfaces/Types: `PascalCase`
- Functions: `camelCase`

**Examples:**
```typescript
✅ // File: MicrophoneButton.tsx
✅ export const MicrophoneButton: React.FC<Props> = () => { }

✅ // File: useConversation.ts
✅ export const useConversation = () => { }

✅ // File: conversation.types.ts
✅ export interface ConversationState { }
✅ export type ConversationStatus = 'active' | 'ended'

❌ microphoneButton.tsx (component files should be PascalCase)
❌ UseConversation.ts (hook files should be camelCase)
❌ export const Conversation = () => {} // in conversation.tsx (confusing naming)
```

### Code Organization

**Backend Endpoint Organization:**
```python
# All endpoints in api/v1/endpoints/{resource}.py follow this pattern:

from fastapi import APIRouter, Depends
from app.models.user import User
from app.schemas.{resource} import {Resource}Create, {Resource}Response
from app.services.{resource}_service import {Resource}Service

router = APIRouter()

# List/Get endpoints first
@router.get("/", response_model=List[{Resource}Response])
async def list_{resources}():
    pass

@router.get("/{id}", response_model={Resource}Response)
async def get_{resource}(id: UUID):
    pass

# Create/Update endpoints
@router.post("/", response_model={Resource}Response)
async def create_{resource}(data: {Resource}Create):
    pass

@router.patch("/{id}", response_model={Resource}Response)
async def update_{resource}(id: UUID, data: {Resource}Update):
    pass

# Delete endpoint last
@router.delete("/{id}")
async def delete_{resource}(id: UUID):
    pass
```

**Frontend Component Organization:**
```typescript
// All components follow this order:

// 1. Imports (external → internal → types)
import React, { useState, useEffect } from 'react'
import { View, Text, StyleSheet } from 'react-native'
import { Button } from '@/components/ui/Button'
import type { ComponentProps } from './types'

// 2. Types/Interfaces (if not in separate file)
interface Props extends ComponentProps {
  onPress: () => void
}

// 3. Component
export const ComponentName: React.FC<Props> = ({ onPress }) => {
  // 3a. Hooks (state, context, custom hooks)
  const [state, setState] = useState()
  const { data } = useCustomHook()

  // 3b. Effects
  useEffect(() => {
    // effect logic
  }, [])

  // 3c. Event handlers
  const handlePress = () => {
    // handler logic
  }

  // 3d. Render helpers (if needed)
  const renderItem = () => <Text>Item</Text>

  // 3e. Main render
  return (
    <View style={styles.container}>
      {/* JSX */}
    </View>
  )
}

// 4. Styles (at bottom)
const styles = StyleSheet.create({
  container: { }
})
```

### Error Handling

**Backend Error Handling Pattern:**

```python
# All services raise specific exceptions
class NumerologyError(Exception):
    pass

class InvalidBirthDateError(NumerologyError):
    pass

# Service layer
class NumerologyService:
    def calculate_life_path(self, birth_date: date) -> int:
        if birth_date > date.today():
            raise InvalidBirthDateError("Birth date cannot be in the future")
        # calculation logic

# API layer catches and converts to HTTP responses
@app.exception_handler(NumerologyError)
async def numerology_error_handler(request: Request, exc: NumerologyError):
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "code": exc.__class__.__name__.upper().replace("ERROR", ""),
                "message": str(exc),
                "retry": False
            }
        }
    )

# Voice pipeline errors
@app.exception_handler(VoicePipelineError)
async def voice_error_handler(request: Request, exc: VoicePipelineError):
    logger.error(f"Voice pipeline error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=503,
        content={
            "success": False,
            "error": {
                "code": "VOICE_SERVICE_UNAVAILABLE",
                "message": "Voice service is temporarily unavailable. Please try again.",
                "retry": True
            }
        }
    )
```

**Frontend Error Handling Pattern:**

```typescript
// All API calls wrapped in try-catch
const useConversation = () => {
  const startConversation = async () => {
    try {
      const response = await conversationService.start()
      // handle success
    } catch (error) {
      if (error.response?.data?.error) {
        const apiError = error.response.data.error
        // Show user-friendly message based on error code
        showError(ERROR_MESSAGES[apiError.code] || apiError.message)

        // Retry if allowed
        if (apiError.retry) {
          // Set up retry logic
        }
      } else {
        // Network error
        showError("Connection failed. Please check your internet.")
      }
    }
  }
}

// User-friendly error messages
const ERROR_MESSAGES = {
  "VOICE_MIC_PERMISSION_DENIED": "We need microphone access to talk with you. Please enable it in settings.",
  "VOICE_CONNECTION_FAILED": "Couldn't connect. Check your internet and try again.",
  "VOICE_STT_UNAVAILABLE": "Having trouble hearing you. Please try again in a moment.",
  "VOICE_LLM_TIMEOUT": "Taking longer than usual. Let me try that again.",
  "VOICE_TTS_UNAVAILABLE": "Having trouble speaking. Please try again.",
  "RATE_LIMIT_EXCEEDED": "You've reached the conversation limit. Please try again later.",
  "AUTH_TOKEN_EXPIRED": "Your session expired. Please sign in again."
}
```

### Logging Strategy

**Backend Logging:**
```python
import structlog

# Configure structured logging
logger = structlog.get_logger()

# All log entries include context
logger.info(
    "conversation_started",
    user_id=user.id,
    conversation_id=conversation.id,
    daily_room_id=room.id
)

logger.error(
    "voice_pipeline_failed",
    user_id=user.id,
    conversation_id=conversation.id,
    error=str(exc),
    service="deepgram"
)

# Log levels
# DEBUG: Development debugging (not in production)
# INFO: Normal operations, state changes
# WARNING: Recoverable issues, degraded performance
# ERROR: Failures requiring attention
# CRITICAL: System-level failures
```

**Frontend Logging:**
```typescript
// Development: console.log
if (__DEV__) {
  console.log('[Conversation] Starting', { conversationId })
}

// Production: Error tracking service (e.g., Sentry)
import * as Sentry from '@sentry/react-native'

Sentry.captureException(error, {
  tags: {
    feature: 'conversation',
    action: 'start'
  },
  extra: {
    userId: user.id,
    conversationId: conversation.id
  }
})
```

---

## Data Architecture

### Database Models

```python
# models/user.py
class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: str
    birth_date: date
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)

    # Relationships
    numerology_profile: Optional["NumerologyProfile"] = Relationship(back_populates="user")
    conversations: List["Conversation"] = Relationship(back_populates="user")

# models/numerology_profile.py
class NumerologyProfile(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", unique=True)
    life_path_number: int
    expression_number: int
    soul_urge_number: int
    birthday_number: int
    personal_year: int
    calculated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    user: User = Relationship(back_populates="numerology_profile")

# models/conversation.py
class Conversation(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    daily_room_id: str = Field(unique=True)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    main_topic: Optional[str] = None
    key_insights: Optional[str] = None
    numbers_discussed: List[int] = Field(default_factory=list, sa_column=Column(ARRAY(Integer)))

    # Relationships
    user: User = Relationship(back_populates="conversations")
    messages: List["ConversationMessage"] = Relationship(back_populates="conversation")

# models/conversation_message.py
class ConversationMessage(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversation.id", index=True)
    role: str = Field(sa_column=Column(Enum("user", "assistant", name="message_role")))
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict = Field(default_factory=dict, sa_column=Column(JSON))

    # Relationship
    conversation: Conversation = Relationship(back_populates="messages")

# models/numerology_interpretation.py
class NumerologyInterpretation(SQLModel, table=True):
    __tablename__ = "numerology_interpretation"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    number_type: str = Field(index=True)  # "life_path", "expression", "soul_urge", "birthday"
    number_value: int = Field(index=True)  # 1-9, 11, 22, 33
    category: str  # "personality", "strengths", "challenges", "career", "relationships"
    content: str = Field(sa_column=Column(Text))
    language: str = Field(default="en", index=True)
    version: int = Field(default=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    __table_args__ = (
        Index('idx_interpretation_lookup', 'number_type', 'number_value', 'language'),
    )
```

### Database Indexes

```sql
-- Performance-critical indexes
CREATE INDEX idx_user_email ON user(email);
CREATE INDEX idx_conversation_user ON conversation(user_id);
CREATE INDEX idx_conversation_started ON conversation(started_at DESC);
CREATE INDEX idx_message_conversation ON conversation_message(conversation_id);
CREATE INDEX idx_interpretation_lookup ON numerology_interpretation(number_type, number_value, language);
```

### Relationships Diagram

```
User (1) ──────────< (1) NumerologyProfile
  │
  │ (1)
  │
  └──────────< (*) Conversation
                │
                │ (1)
                │
                └──────────< (*) ConversationMessage

NumerologyInterpretation (standalone reference table)
```

---

## API Contracts

### Authentication Endpoints

```typescript
POST /api/v1/auth/register
Request: {
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "John Smith",
  "birth_date": "1990-05-15"
}
Response: {
  "success": true,
  "data": {
    "user": { "id": "uuid", "email": "...", "full_name": "..." },
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "token_type": "bearer",
    "expires_in": 900
  }
}

POST /api/v1/auth/login
Request: {
  "email": "user@example.com",
  "password": "SecurePass123!"
}
Response: {
  "success": true,
  "data": {
    "user": { ... },
    "access_token": "eyJ...",
    "refresh_token": "eyJ..."
  }
}

POST /api/v1/auth/refresh
Request: {
  "refresh_token": "eyJ..."
}
Response: {
  "success": true,
  "data": {
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "expires_in": 900
  }
}

POST /api/v1/auth/google
Request: {
  "id_token": "google_oauth_token"
}
Response: {
  "success": true,
  "data": {
    "user": { ... },
    "access_token": "eyJ...",
    "refresh_token": "eyJ..."
  }
}
```

### Conversation Endpoints

```typescript
POST /api/v1/conversations/start
Headers: {
  "Authorization": "Bearer eyJ..."
}
Response: {
  "success": true,
  "data": {
    "conversation_id": "uuid",
    "daily_room_url": "https://example.daily.co/room-name",
    "daily_token": "token",
    "expires_at": "2025-11-03T15:30:00Z"
  }
}

POST /api/v1/conversations/{id}/end
Request: {
  "duration_seconds": 300,
  "main_topic": "Life path number discussion",
  "key_insights": "User is a Life Path 7, focusing on spiritual growth",
  "numbers_discussed": [7, 22, 5]
}
Response: {
  "success": true,
  "data": {
    "conversation": {
      "id": "uuid",
      "started_at": "2025-11-03T14:30:00Z",
      "ended_at": "2025-11-03T14:35:00Z",
      "duration_seconds": 300,
      "main_topic": "...",
      "key_insights": "..."
    }
  }
}

GET /api/v1/conversations?page=1&limit=20
Response: {
  "success": true,
  "data": [
    {
      "id": "uuid",
      "started_at": "2025-11-03T14:30:00Z",
      "ended_at": "2025-11-03T14:35:00Z",
      "duration_seconds": 300,
      "main_topic": "Life path number discussion"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 45,
    "pages": 3
  }
}

GET /api/v1/conversations/{id}
Response: {
  "success": true,
  "data": {
    "id": "uuid",
    "started_at": "...",
    "ended_at": "...",
    "duration_seconds": 300,
    "main_topic": "...",
    "key_insights": "...",
    "numbers_discussed": [7, 22, 5],
    "messages": [
      {
        "role": "user",
        "content": "What's my life path number?",
        "timestamp": "2025-11-03T14:30:15Z"
      },
      {
        "role": "assistant",
        "content": "Based on your birth date, your Life Path number is 7...",
        "timestamp": "2025-11-03T14:30:18Z"
      }
    ]
  }
}

DELETE /api/v1/conversations/{id}
Response: {
  "success": true,
  "message": "Conversation deleted successfully"
}
```

### Numerology Endpoints

```typescript
GET /api/v1/numerology/profile
Response: {
  "success": true,
  "data": {
    "life_path_number": 7,
    "expression_number": 5,
    "soul_urge_number": 3,
    "birthday_number": 15,
    "personal_year": 9,
    "calculated_at": "2025-11-03T10:00:00Z"
  }
}

POST /api/v1/numerology/calculate
Request: {
  "type": "life_path",
  "data": {
    "birth_date": "1990-05-15"
  }
}
Response: {
  "success": true,
  "data": {
    "number_type": "life_path",
    "value": 7,
    "interpretation": {
      "personality": "Analytical, introspective, spiritual seeker",
      "strengths": "Deep thinker, intuitive, wisdom-oriented",
      "challenges": "Can be isolated, overthinks, struggles with trust",
      "career": "Research, teaching, spirituality, analysis",
      "relationships": "Needs independence, values depth over quantity"
    }
  }
}

GET /api/v1/numerology/interpret/life_path/7
Response: {
  "success": true,
  "data": {
    "number_type": "life_path",
    "value": 7,
    "interpretation": {
      "personality": "...",
      "strengths": "...",
      "challenges": "...",
      "career": "...",
      "relationships": "..."
    }
  }
}
```

---

## Security Architecture

### Authentication & Authorization

**JWT Token Strategy:**
- **Access Token**: 15 minutes lifetime, used for API authentication
- **Refresh Token**: 7 days lifetime, used to get new access tokens
- **Algorithm**: HS256 (symmetric)
- **Secret**: Environment variable, rotated quarterly
- **Storage**:
  - Backend: Refresh tokens in Redis with user_id mapping
  - Frontend: Expo SecureStore (encrypted on device)

**OAuth Integration:**
- **Provider**: Google OAuth 2.0
- **Flow**: Authorization Code Flow
- **Scopes**: email, profile
- **Verification**: Backend verifies Google ID token before issuing JWT

### Data Security

**Encryption at Rest:**
- **Database**: PostgreSQL with encryption enabled
- **Passwords**: bcrypt with cost factor 12
- **Sensitive Config**: Environment variables, never committed to Git
- **Redis**: Encryption in transit (TLS) and at rest (Azure managed)

**Encryption in Transit:**
- **API Communication**: HTTPS only (TLS 1.3)
- **WebRTC Streams**: DTLS-SRTP encryption via Daily.co
- **Database Connection**: SSL/TLS required

### Privacy Controls

**GDPR Compliance:**
- **Right to Access**: GET /api/v1/users/me/export returns all user data
- **Right to Deletion**: DELETE /api/v1/users/me removes all user data
- **Data Minimization**: No raw voice recordings stored (only transcriptions)
- **Consent**: Clear privacy policy, opt-in for data improvement
- **Retention**: Conversation history retained for 30 days, then archived/deleted

**Voice Data Privacy:**
- **No Persistent Storage**: Voice audio not saved (privacy-first)
- **Transcription Only**: Text transcriptions stored for context
- **Opt-in Recording**: Future feature with explicit user consent
- **Data Location**: All data in Azure EU regions for GDPR compliance

### API Security

**Rate Limiting (Redis-based):**
```python
# Endpoints have different rate limits
rate_limits = {
    "/api/v1/auth/login": "5 per minute",          # Prevent brute force
    "/api/v1/auth/register": "3 per hour",         # Prevent spam accounts
    "/api/v1/conversations/start": "10 per hour",  # Manage costs + abuse
    "/api/v1/numerology/*": "60 per hour",         # General API limit
}
```

**Input Validation:**
- **Pydantic Models**: All request bodies validated
- **SQL Injection**: SQLModel ORM prevents injection
- **XSS**: API returns JSON only, frontend sanitizes any HTML
- **CSRF**: Not needed (stateless JWT auth, no cookies)

**CORS Configuration:**
```python
# Only allow frontend domains
allowed_origins = [
    "https://numerologist-ai.com",          # Production web
    "https://*.expo.dev",                   # Expo development
    "exp://localhost:8081",                 # Local development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

---

## Performance Considerations

### Latency Targets (from NFR-P1)

**Voice Pipeline Latency (<3 seconds end-to-end):**
- Speech-to-Text (Deepgram): <800ms
- AI Processing (GPT-5-mini): <1500ms
- Text-to-Speech (ElevenLabs): <700ms
- Network overhead: ~200ms

**Optimization Strategies:**

1. **Redis Caching:**
   ```python
   # Numerology interpretations cached for 24 hours
   interpretation = await redis.get(f"interp:{number_type}:{value}")
   if not interpretation:
       interpretation = await db.fetch_interpretation(number_type, value)
       await redis.set(f"interp:{number_type}:{value}", interpretation, ex=86400)
   ```

2. **Async Operations:**
   ```python
   # All I/O operations use async/await
   async def get_user_context(user_id: str):
       # Run in parallel
       user, profile, recent_conversations = await asyncio.gather(
           db.get_user(user_id),
           numerology_service.get_profile(user_id),
           db.get_recent_conversations(user_id, limit=5)
       )
   ```

3. **Connection Pooling:**
   ```python
   # PostgreSQL connection pool
   engine = create_async_engine(
       DATABASE_URL,
       pool_size=20,
       max_overflow=10,
       pool_pre_ping=True
   )

   # Redis connection pool
   redis_client = redis.Redis(
       connection_pool=redis.ConnectionPool(
           host=REDIS_HOST,
           port=REDIS_PORT,
           max_connections=50
       )
   )
   ```

4. **Pipecat Pipeline Optimization:**
   - Pre-warm LLM connections
   - Stream TTS audio (don't wait for complete generation)
   - Use VAD (Voice Activity Detection) to reduce silence processing

### Database Performance

**Query Optimization:**
```python
# Use indexes for frequent queries
@router.get("/conversations")
async def list_conversations(
    user_id: UUID,
    page: int = 1,
    limit: int = 20
):
    # Index on (user_id, started_at DESC) makes this fast
    conversations = await db.query(
        Conversation,
        Conversation.user_id == user_id
    ).order_by(
        Conversation.started_at.desc()
    ).offset((page - 1) * limit).limit(limit).all()
```

**Batch Operations:**
```python
# Seed numerology interpretations in batches
async def seed_interpretations(interpretations: List[NumerologyInterpretation]):
    # Insert 100 at a time
    for batch in chunks(interpretations, 100):
        await db.bulk_insert(batch)
```

### Frontend Performance

**React Native Optimizations:**
```typescript
// Memoize expensive components
const MicrophoneButton = React.memo(({ onPress, isActive }) => {
  // Only re-renders when isActive changes
})

// Lazy load screens
const HistoryScreen = React.lazy(() => import('./screens/HistoryScreen'))

// Optimize list rendering
<FlatList
  data={conversations}
  renderItem={renderConversation}
  keyExtractor={(item) => item.id}
  initialNumToRender={10}
  maxToRenderPerBatch={10}
  windowSize={5}
/>
```

**React Query Caching:**
```typescript
// Cache API responses, background refetch
const { data: profile } = useQuery({
  queryKey: ['numerology', 'profile'],
  queryFn: fetchNumerologyProfile,
  staleTime: 1000 * 60 * 60, // 1 hour
  cacheTime: 1000 * 60 * 60 * 24, // 24 hours
})
```

---

## Deployment Architecture

### Development Environment

**Local Development:**
```bash
# Backend (FastAPI + Pipecat)
cd numerologist-ai-backend
docker-compose up  # Starts PostgreSQL, Redis, backend
# Access: http://localhost:8000

# Frontend (Expo)
cd numerologist-ai
npm start  # Starts Expo development server
# Access: http://localhost:8081 or scan QR code
```

### Production Deployment (Azure)

**Infrastructure Components:**

```
┌─────────────────────────────────────────────────────────┐
│                     Azure Cloud                         │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │           Frontend (Expo + Web)                  │  │
│  │  - Expo EAS Build (Android APK/AAB)             │  │
│  │  - Azure Static Web Apps (PWA)                  │  │
│  │  - CDN: Azure Front Door                        │  │
│  └──────────────────────────────────────────────────┘  │
│                         │                               │
│                         │ HTTPS                         │
│                         ▼                               │
│  ┌──────────────────────────────────────────────────┐  │
│  │           API Gateway / Load Balancer            │  │
│  │  - Azure Application Gateway                     │  │
│  │  - SSL/TLS Termination                          │  │
│  └──────────────────────────────────────────────────┘  │
│                         │                               │
│                         ▼                               │
│  ┌──────────────────────────────────────────────────┐  │
│  │         FastAPI Backend (Container Apps)         │  │
│  │  - Auto-scaling: 2-10 instances                 │  │
│  │  - Health checks + rolling updates              │  │
│  └──────────────────────────────────────────────────┘  │
│         │                                │              │
│         │                                │              │
│         ▼                                ▼              │
│  ┌──────────────┐              ┌──────────────────┐   │
│  │  PostgreSQL  │              │  Redis Cache     │   │
│  │  (Azure DB)  │              │  (Azure Cache)   │   │
│  │  - Managed   │              │  - Managed       │   │
│  │  - Backups   │              │  - HA enabled    │   │
│  └──────────────┘              └──────────────────┘   │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Pipecat Bot Workers                      │  │
│  │  - Azure Container Instances (on-demand)        │  │
│  │  - Spawned per conversation                     │  │
│  │  - Auto-cleanup after conversation              │  │
│  └──────────────────────────────────────────────────┘  │
│         │                                               │
│         └──── WebRTC ────────> Daily.co (External)     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Deployment Steps:**

1. **Backend (Docker + Azure Container Apps):**
```bash
# Build Docker image
docker build -t numerologist-ai-backend:latest .

# Push to Azure Container Registry
az acr build --registry myregistry --image numerologist-ai-backend:latest .

# Deploy to Azure Container Apps
az containerapp create \
  --name numerologist-ai-api \
  --resource-group numerologist-rg \
  --image myregistry.azurecr.io/numerologist-ai-backend:latest \
  --target-port 8000 \
  --ingress external \
  --env-vars \
    DATABASE_URL="$DATABASE_URL" \
    REDIS_URL="$REDIS_URL" \
    AZURE_OPENAI_KEY="$OPENAI_KEY" \
  --min-replicas 2 \
  --max-replicas 10
```

2. **Frontend (Expo EAS):**
```bash
# Android APK/AAB
eas build --platform android --profile production

# Submit to Google Play Store
eas submit --platform android --latest

# Web PWA
npm run build:web
az storage blob upload-batch -s ./web-build -d $web-container
```

3. **Database & Cache:**
```bash
# PostgreSQL (Azure Database for PostgreSQL)
az postgres flexible-server create \
  --name numerologist-db \
  --resource-group numerologist-rg \
  --sku-name Standard_B2s \
  --version 14 \
  --backup-retention 30

# Redis (Azure Cache for Redis)
az redis create \
  --name numerologist-cache \
  --resource-group numerologist-rg \
  --sku Basic \
  --vm-size c0
```

### CI/CD Pipeline (GitHub Actions)

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build and push Docker image
        run: |
          docker build -t numerologist-ai-backend:${{ github.sha }} .
          docker push myregistry.azurecr.io/numerologist-ai-backend:${{ github.sha }}
      - name: Deploy to Azure Container Apps
        run: |
          az containerapp update \
            --name numerologist-ai-api \
            --image myregistry.azurecr.io/numerologist-ai-backend:${{ github.sha }}

  frontend-android:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Expo
        uses: expo/expo-github-action@v8
      - name: Build Android
        run: eas build --platform android --non-interactive --no-wait
```

### Monitoring & Observability

**Application Insights (Azure):**
- API request/response times
- Error rates and exceptions
- Voice pipeline latency tracking
- User session analytics

**Logging:**
- Structured JSON logs → Azure Log Analytics
- Voice conversation events tracked
- Error tracking with stack traces

**Alerts:**
- Voice latency >5 seconds (95th percentile)
- API error rate >5%
- Database connection failures
- Redis cache misses >50%

---

## Development Environment

### Prerequisites

**Required Software:**
- **Node.js**: v18+ (for frontend)
- **Python**: 3.10+ (for backend)
- **Docker Desktop**: Latest (for PostgreSQL, Redis)
- **Git**: Latest
- **Expo CLI**: `npm install -g expo-cli`
- **pipx**: For Python tools (`pip install pipx`)

**Optional:**
- **VSCode**: Recommended IDE
- **Postman**: API testing
- **TablePlus/pgAdmin**: Database GUI

**API Keys Required:**
- Azure OpenAI API key
- Deepgram API key
- ElevenLabs API key
- Daily.co API key
- Google OAuth credentials (for OAuth)

### Setup Commands

```bash
# 1. Clone repository
git clone https://github.com/yourusername/numerologist-ai.git
cd numerologist-ai

# 2. Backend Setup
cd numerologist-ai-backend

# Copy environment template
cp .env.example .env
# Edit .env and add your API keys

# Start PostgreSQL + Redis
docker-compose up -d postgres redis

# Install Python dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Seed numerology interpretations
python -m app.scripts.seed_interpretations

# Start backend
uvicorn app.main:app --reload
# Access: http://localhost:8000
# API Docs: http://localhost:8000/docs

# 3. Frontend Setup
cd ../numerologist-ai

# Install dependencies
npm install

# Copy environment template
cp .env.example .env
# Edit .env and add backend URL

# Start Expo development server
npm start
# Scan QR code with Expo Go app or press 'w' for web

# 4. Run Tests
# Backend tests
cd numerologist-ai-backend
pytest

# Frontend tests
cd numerologist-ai
npm test
```

### Development Workflow

**Starting Development:**
```bash
# Terminal 1: Backend
cd numerologist-ai-backend
docker-compose up postgres redis  # Start dependencies
uvicorn app.main:app --reload     # Start API

# Terminal 2: Frontend
cd numerologist-ai
npm start  # Start Expo

# Terminal 3: Logs/Tests
# Run tests, check logs, etc.
```

**Creating Database Migrations:**
```bash
# After modifying models
cd numerologist-ai-backend
alembic revision --autogenerate -m "Add new field to user table"
alembic upgrade head
```

**Testing Voice Pipeline Locally:**
```bash
# Create a test Daily.co room
python -m app.scripts.test_voice_pipeline

# This will:
# 1. Create a Daily room
# 2. Spawn Pipecat bot
# 3. Print room URL for testing
# 4. Join with browser or Expo app
```

---

## Architecture Decision Records (ADRs)

### ADR-001: Use Pipecat-ai for Voice Pipeline Orchestration

**Status:** Accepted

**Context:**
We need to orchestrate multiple voice AI services (Deepgram STT, OpenAI LLM, ElevenLabs TTS) with <3 second end-to-end latency. Building custom orchestration would be complex and error-prone.

**Decision:**
Use Pipecat-ai framework to handle voice pipeline orchestration, LLM context management, and function calling.

**Consequences:**
- ✅ Reduces custom code, leverages battle-tested framework
- ✅ Built-in support for Daily.co, Deepgram, OpenAI, ElevenLabs
- ✅ Handles complex state management (user speaking, AI responding, interrupts)
- ✅ Function calling for numerology tools works out-of-the-box
- ⚠️ Dependency on framework updates and maintenance
- ⚠️ Learning curve for framework patterns

**Alternatives Considered:**
- Custom pipeline: Too complex, high maintenance
- LangChain: Not optimized for real-time voice

---

### ADR-002: PostgreSQL for Numerology Knowledge Base

**Status:** Accepted

**Context:**
Numerology interpretations need to be stored and retrieved quickly. Options: hardcoded in Python, JSON files, or database.

**Decision:**
Use PostgreSQL to store numerology interpretations, cached in Redis for fast access.

**Consequences:**
- ✅ Can update interpretations without code deployment
- ✅ Enables future features (A/B testing interpretations, multiple languages)
- ✅ Queryable and maintainable
- ✅ Source of truth separate from code
- ⚠️ Adds ~10-50ms latency (mitigated by Redis caching)
- ⚠️ Requires database seeding script

**Alternatives Considered:**
- Hardcoded: Fastest but inflexible
- JSON files: Still requires deployment for updates

---

### ADR-003: Zustand for Frontend State Management

**Status:** Accepted

**Context:**
React Native app needs state management for auth, conversation, and voice state. Options: Context API, Redux, Zustand, MobX.

**Decision:**
Use Zustand for global state management.

**Consequences:**
- ✅ Minimal boilerplate (simpler than Redux)
- ✅ 1kb bundle size (lightweight)
- ✅ No Context provider nesting hell
- ✅ Easy to test and debug
- ✅ Works great with TypeScript
- ⚠️ Less mature ecosystem than Redux (fewer dev tools)

**Alternatives Considered:**
- Context API: Too much nesting for multiple contexts
- Redux: Over-engineered for Level 2 project

---

### ADR-004: Merged Conversation + Voice Session Endpoints

**Status:** Accepted

**Context:**
Initially designed separate endpoints for conversation data (business layer) and voice infrastructure (Daily.co rooms). User questioned the complexity.

**Decision:**
Merge into single `/conversations` endpoint that handles both conversation record creation and Daily.co room setup.

**Consequences:**
- ✅ Simpler API surface (fewer endpoints)
- ✅ Atomic operations (conversation + room created together)
- ✅ Less room for error (can't forget to create room)
- ✅ Better for Level 2 project scope
- ⚠️ Slight coupling of business and infrastructure logic

**Alternatives Considered:**
- Separate endpoints: More complex, no real benefit for this use case

---

### ADR-005: Azure OpenAI GPT-5-mini over GPT-4o-mini

**Status:** Accepted

**Context:**
Initially suggested GPT-4o-mini-realtime-preview. User corrected that GPT-5-mini exists and is available on Azure.

**Decision:**
Use Azure OpenAI GPT-5-mini for LLM reasoning.

**Consequences:**
- ✅ Latest model with improved reasoning
- ✅ Real-time optimized for voice agents
- ✅ Function calling for numerology tools
- ✅ Cost-effective (mini variant)
- ⚠️ Requires Azure OpenAI service setup
- ⚠️ Model availability limited to certain regions (East US 2, Sweden Central)

**Alternatives Considered:**
- GPT-4o-mini: Older model, less optimized for real-time
- GPT-4.1-mini: Newer but lacks realtime preview optimizations

---

_Generated by BMAD Decision Architecture Workflow v1.3_
_Date: 2025-11-03_
_For: Hieu_
