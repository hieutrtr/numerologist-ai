# Quick Start Guide
## Get Your Voice Bot Running in 10 Minutes

This guide gets you from zero to a working voice bot as quickly as possible.

## Prerequisites

- Python 3.11+
- API keys (see [API Keys](#api-keys) below)

## 5-Minute Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
DEEPGRAM_API_KEY=your_key_here
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
ELEVENLABS_API_KEY=your_key_here
DAILY_API_KEY=your_key_here
```

### 3. Start the Server

```bash
uvicorn main:app --reload
```

You should see:

```
INFO: Started server process [12345]
INFO: Uvicorn running on http://127.0.0.1:8000
```

### 4. Test the API

Open http://localhost:8000/docs in your browser.

Try the `/health` endpoint - you should get:

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development"
}
```

### 5. Start a Conversation

**Option A: Using Swagger UI** (http://localhost:8000/docs)
1. Expand `POST /api/v1/conversations/start`
2. Click "Try it out"
3. Click "Execute"
4. Copy the `daily_room_url` from the response

**Option B: Using curl**

```bash
curl -X POST http://localhost:8000/api/v1/conversations/start
```

### 6. Join the Voice Call

1. Open the `daily_room_url` in your browser
2. Allow microphone access
3. Say "Hello"
4. The bot should respond!

---

## API Keys

You need accounts with these services:

| Service | Purpose | Sign Up | Free Tier |
|---------|---------|---------|-----------|
| **Deepgram** | Speech-to-text | [console.deepgram.com](https://console.deepgram.com/) | $200 credit |
| **Azure OpenAI** | Language model | [portal.azure.com](https://portal.azure.com/) | Varies |
| **ElevenLabs** | Text-to-speech | [elevenlabs.io](https://elevenlabs.io/) | 10k chars/month |
| **Daily.co** | WebRTC rooms | [dashboard.daily.co](https://dashboard.daily.co/) | 100 rooms/month |

### Getting API Keys

#### Deepgram (Speech-to-Text)
1. Go to https://console.deepgram.com/
2. Sign up / Log in
3. Navigate to "API Keys" in sidebar
4. Click "Create a New API Key"
5. Copy the key (starts with a long string)

#### Azure OpenAI (Language Model)
1. Go to https://portal.azure.com/
2. Create an "Azure OpenAI" resource
3. Once deployed, go to "Keys and Endpoint"
4. Copy:
   - Key 1 → `AZURE_OPENAI_API_KEY`
   - Endpoint → `AZURE_OPENAI_ENDPOINT`
5. Go to "Model deployments" and deploy a GPT-4 model
6. Copy deployment name → `AZURE_OPENAI_MODEL_DEPLOYMENT_NAME`

#### ElevenLabs (Text-to-Speech)
1. Go to https://elevenlabs.io/
2. Sign up / Log in
3. Click your profile icon
4. Select "Profile"
5. Copy API key from "API Key" section

#### Daily.co (WebRTC)
1. Go to https://dashboard.daily.co/
2. Sign up / Log in
3. Navigate to "Developers" → "API Keys"
4. Copy your API key (starts with `daily_`)

---

## Test Your Setup

### 1. Verify Configuration

```bash
python -c "from core.settings import settings; print('✅ Config loaded successfully')"
```

### 2. Check API Keys

```bash
python -c "
from core.settings import settings
print('Deepgram:', '✅' if settings.deepgram_api_key else '❌')
print('Azure OpenAI:', '✅' if settings.azure_openai_api_key else '❌')
print('ElevenLabs:', '✅' if settings.elevenlabs_api_key else '❌')
print('Daily.co:', '✅' if settings.daily_api_key else '❌')
"
```

### 3. Test Voice Pipeline

```bash
cd backend
python -c "
import asyncio
from services.daily_service import create_room

async def test():
    print('Testing Daily.co room creation...')
    room = await create_room('test-room')
    print(f'✅ Room created: {room[\"room_url\"]}')

asyncio.run(test())
"
```

---

## What's Next?

Now that your bot is running, customize it:

1. **Add Functions**: Edit `voice_pipeline/function_schemas.py` and `function_handlers.py`
2. **Customize Prompt**: Edit `voice_pipeline/pipecat_bot.py` → `_get_system_prompt()`
3. **Change Language**: Set `VOICE_LANGUAGE=vi` in `.env` for Vietnamese
4. **Add Auth**: Implement user authentication in `api/endpoints/conversations.py`

See [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) for detailed instructions.

---

## Troubleshooting

### "Module not found" Error

```bash
pip install -r requirements.txt
```

### "Invalid API Key" Error

- Check your `.env` file
- Ensure keys are copied correctly (no extra spaces)
- Verify keys are active in respective dashboards

### Bot Doesn't Respond

- Check console logs for errors
- Verify all 4 API keys are set
- Test each service individually

### No Audio in Browser

- Allow microphone permissions
- Check browser console for WebRTC errors
- Try Chrome (best Daily.co support)

### Still Stuck?

Check the full [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) or review logs:

```bash
# In backend directory
uvicorn main:app --reload --log-level debug
```

---

## Next Steps

- **Full Guide**: [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)
- **Architecture**: [README.md](README.md)
- **API Docs**: http://localhost:8000/docs

Happy building! 🎙️🤖