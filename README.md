# Numerologist AI

A voice-first conversational AI platform that provides personalized numerology readings through natural conversation.

## Overview

**Numerologist AI** is an innovative application that combines modern AI technology with the ancient art of numerology. Users can have real-time voice conversations with an AI numerologist who:

- Calculates your Life Path, Expression, Soul Urge, and other numerology numbers
- Interprets the meaning and significance of your numbers
- Provides personalized guidance based on numerological principles
- Remembers past conversations and builds on previous insights

**Voice-First Experience:** All interactions are optimized for natural speech, making numerology accessible through conversational AI rather than text-based interfaces.

---

## Tech Stack

### Backend
- **Framework:** FastAPI (Python)
- **Database:** PostgreSQL + Redis caching
- **Voice Pipeline:** Pipecat-ai orchestrating:
  - Deepgram (Speech-to-Text)
  - Azure OpenAI GPT-5-mini (LLM reasoning)
  - ElevenLabs (Text-to-Speech)
  - Daily.co (WebRTC infrastructure)
- **Package Manager:** uv (fast Python package management)

### Frontend
- **Framework:** React Native + Expo
- **Platforms:** Web (PWA) + Android native
- **Language:** TypeScript
- **State Management:** Zustand
- **API Client:** Axios + React Query

### Infrastructure
- **Deployment:** Azure
- **Container Runtime:** Docker/Docker Compose (local development)
- **Authentication:** JWT tokens
- **Rate Limiting & Caching:** Redis

---

## Quick Start

### Prerequisites

- **Python 3.10+** with `uv` package manager
- **Node.js 18+** with npm
- **Docker & Docker Compose** (for local PostgreSQL + Redis)
- **Git**

### Setup

1. **Clone and Enter Project:**
   ```bash
   git clone https://github.com/yourusername/numerologist-ai.git
   cd numerologist-ai
   ```

2. **Create Environment Files:**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your API keys (Daily, Deepgram, Azure OpenAI, ElevenLabs)

3. **Start Development Environment:**
   ```bash
   make dev
   ```

   This command will:
   - Start PostgreSQL + Redis via Docker
   - Launch FastAPI backend on `http://localhost:8000`
   - Launch Expo dev server for mobile app

4. **Access the Services:**
   - **Backend API:** http://localhost:8000
   - **API Documentation:** http://localhost:8000/docs
   - **Mobile App (Web):** Press 'w' in Expo terminal, or scan QR code

---

## Project Structure

```
numerologist-ai/                    # Root monorepo
├── backend/                        # Python FastAPI backend
│   ├── src/
│   │   ├── api/                   # API endpoints
│   │   ├── models/                # Database models
│   │   ├── services/              # Business logic
│   │   ├── voice_pipeline/        # Pipecat bot implementation
│   │   └── core/                  # Configuration & utilities
│   └── pyproject.toml             # Python dependencies
│
├── mobile/                         # React Native + Expo frontend
│   ├── src/
│   │   ├── app/                   # Routes & screens
│   │   ├── components/            # UI components
│   │   ├── services/              # API client
│   │   └── stores/                # State management
│   └── package.json               # Node dependencies
│
├── Makefile                        # Development commands
├── docker-compose.yml              # Local services
├── .gitignore                      # Git ignore rules
└── README.md                       # This file
```

---

## Development Commands

Use the Makefile for common development tasks:

```bash
make help          # Show all available commands
make dev           # Start full development environment
make backend       # Start backend only
make mobile        # Start mobile app only
make docker-up     # Start PostgreSQL + Redis
make docker-down   # Stop Docker services
make test          # Run all tests
make clean         # Clean generated files
```

---

## API Documentation

Once running, visit `http://localhost:8000/docs` for interactive Swagger documentation of all API endpoints.

### Key Endpoints

- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/users/me` - Get current user
- `POST /api/v1/conversations/start` - Start voice conversation
- `GET /api/v1/conversations` - View conversation history

---

## First Conversation

1. Register account: Provide email, password, name, and birth date
2. Tap "Start Conversation" on home screen
3. Grant microphone permission when prompted
4. Ask "What's my life path number?" or any numerology question
5. AI calculates from your birth date and provides personalized interpretation
6. Continue natural conversation to explore your numbers deeper

---

## Features

✅ **Authentication:** Secure JWT-based user accounts
✅ **Voice Interaction:** Real-time speech input/output
✅ **Numerology Calculations:** Life Path, Expression, Soul Urge, and more
✅ **Conversation History:** View and review past sessions
✅ **Cross-Platform:** Web PWA and native Android support
✅ **Offline Support:** PWA can work offline (limited features)
✅ **Data Privacy:** GDPR-compliant data export and deletion
✅ **Rate Limiting:** API abuse prevention

---

## Environment Variables

See `.env.example` for complete configuration. Required variables:

- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `JWT_SECRET` - Secret for JWT token signing
- `DAILY_API_KEY` - Daily.co API key
- `DEEPGRAM_API_KEY` - Deepgram API key
- `AZURE_OPENAI_API_KEY` - Azure OpenAI API key
- `AZURE_OPENAI_ENDPOINT` - Azure OpenAI endpoint
- `ELEVENLABS_API_KEY` - ElevenLabs API key

---

## Testing

Run tests for backend and frontend:

```bash
make test
```

Or individually:

```bash
# Backend tests
cd backend && uv run pytest

# Frontend tests
cd mobile && npm test
```

---

## Deployment

### Production Deployment

Backend is deployed to Azure Container Apps with:
- Managed PostgreSQL database
- Azure Cache for Redis
- Application Insights monitoring

Frontend is deployed as:
- PWA to Azure Static Web Apps
- Android APK via Expo EAS to Google Play Store

### Manual Deployment

See `docs/deployment.md` for detailed deployment instructions.

---

## Documentation

- **Architecture:** `docs/architecture.md` - System design and tech decisions
- **Epics:** `docs/epics.md` - Feature breakdown and development roadmap
- **PRD:** `docs/PRD.md` - Product requirements and business goals

---

## Contributing

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes and test locally
3. Commit with clear message: `git commit -m "Add feature description"`
4. Push branch and create pull request

---

## Troubleshooting

### Backend won't start
- Check PostgreSQL/Redis are running: `docker ps`
- Check `.env` file has required variables
- Check port 8000 is available

### Microphone permission issues
- Grant permissions in app settings
- On Android, go to Settings → Apps → Numerologist AI → Permissions

### Voice latency too high
- Check internet connection quality
- Reduce background network activity
- This is being optimized in future releases

---

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Email support@numerologist-ai.com
- Join our Discord community

---

## License

MIT License - see LICENSE file for details

---

## Acknowledgments

Built with modern open-source technologies:
- FastAPI, React Native, Pipecat-ai
- Deepgram, Azure OpenAI, ElevenLabs, Daily.co

---

**Ready to discover your numbers?** Start the dev environment and begin exploring! 🔮

```bash
make dev
```

Happy exploring! 🚀
