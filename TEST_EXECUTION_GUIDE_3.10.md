# Story 3.10: End-to-End Voice Test - Execution Guide

**Story ID:** 3-10-end-to-end-voice-test
**Status:** in-progress
**Date Started:** 2025-11-10

This guide provides step-by-step instructions for executing Story 3.10 manual tests with comprehensive logging setup.

---

## Table of Contents

1. [Pre-Test Environment Setup](#pre-test-environment-setup)
2. [Logging Configuration](#logging-configuration)
3. [Test Execution Flow](#test-execution-flow)
4. [Result Recording Template](#result-recording-template)
5. [Troubleshooting](#troubleshooting)

---

## Pre-Test Environment Setup

### Task 1: Verify Environment Configuration

#### 1.1 Check Backend Environment Variables

```bash
# Navigate to backend directory
cd /Users/hieutt50/projects/numerologist-ai/backend

# Check if .env file exists
ls -la .env

# Verify required API keys are set
grep -E "DAILY_API_KEY|DEEPGRAM_API_KEY|AZURE_OPENAI_API_KEY|ELEVENLABS_API_KEY" .env
```

**Required Variables:**
- ✓ `DAILY_API_KEY` - Daily.co API key for room management
- ✓ `DEEPGRAM_API_KEY` - Deepgram for speech-to-text
- ✓ `AZURE_OPENAI_API_KEY` - Azure OpenAI for LLM
- ✓ `AZURE_OPENAI_ENDPOINT` - Azure OpenAI endpoint URL
- ✓ `ELEVENLABS_API_KEY` - ElevenLabs for text-to-speech

**Action:** If any are missing, update `.env` file and save.

#### 1.2 Start Backend Server with Logging

```bash
# Terminal 1: Start backend with uvicorn (with reload for development)
cd /Users/hieutt50/projects/numerologist-ai/backend
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application startup complete
```

**Keep this terminal open** - you'll monitor logs here during testing.

#### 1.3 Start Frontend Dev Server

```bash
# Terminal 2: Start mobile/frontend web server
cd /Users/hieutt50/projects/numerologist-ai/mobile
npm run web

# Expected output:
# Local:   http://localhost:8081
# Expo Go: exp://...
```

**Keep this terminal open** - frontend should be accessible at `http://localhost:8081`

#### 1.4 Verify Database and Migrations

```bash
# Terminal 3: Check database connection and run migrations
cd /Users/hieutt50/projects/numerologist-ai/backend

# Run migrations to ensure schema is up-to-date
uv run alembic upgrade head

# Expected output:
# INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
# INFO  [alembic.runtime.migration] Will assume transactional DDL.
```

#### 1.5 Clear Old Test Data (Optional)

```bash
# Connect to PostgreSQL and clear old conversations
psql -U postgres -d numerologist_ai -c "DELETE FROM conversation WHERE created_at < NOW() - INTERVAL '1 day';"

# Verify conversations table is accessible
psql -U postgres -d numerologist_ai -c "SELECT COUNT(*) FROM conversation;"
```

#### 1.6 Open Daily.co Dashboard

- Navigate to: https://dashboard.daily.co/
- Login with your Daily.co account
- Keep this open in a browser tab to monitor room creation/deletion during tests

**✅ All environment checks complete** - You're ready for testing!

---

## Logging Configuration

### Backend Logging Setup

The backend is configured with structured logging. Monitor the terminal running uvicorn for these log patterns:

#### Key Log Patterns to Watch For

**Conversation Start:**
```
INFO:     POST /api/v1/conversations/start for user {user_id}
INFO:     Creating conversation {conversation_id} for user {user_id}
INFO:     Created Daily.co room: {room_name}
INFO:     Spawning Pipecat bot for conversation {conversation_id}
INFO:     Bot spawned for conversation {conversation_id}
```

**Speech-to-Text (Deepgram):**
```
INFO:     [Deepgram] Transcription: "Hello"
INFO:     [Deepgram] Confidence: 0.95
DEBUG:    STT latency: 234ms
```

**LLM Response (Azure OpenAI):**
```
INFO:     [Azure OpenAI] Sending prompt: "Hello"
INFO:     [Azure OpenAI] Response: "Hello! How can I help you today?"
DEBUG:    LLM latency: 1250ms
```

**Text-to-Speech (ElevenLabs):**
```
INFO:     [ElevenLabs] Generating speech for: "Hello! How can I help you today?"
INFO:     [ElevenLabs] Audio generated successfully
DEBUG:    TTS latency: 450ms
```

**Conversation End:**
```
INFO:     Attempting to end conversation {conversation_id} for user {user_id}
INFO:     Conversation {conversation_id} ended successfully. Duration: 45 seconds
INFO:     Successfully deleted Daily.co room: {room_name}
```

### Enable Verbose Logging (Optional)

To capture more detailed logs, you can set logging level to DEBUG:

```bash
# Edit backend/src/core/config.py or set environment variable
export LOG_LEVEL=DEBUG

# Restart backend server
uv run uvicorn src.main:app --reload --log-level debug --host 0.0.0.0 --port 8000
```

---

## Test Execution Flow

### Task 2: Execute End-to-End Test Flow

#### 2.1 Login to App

1. Open browser to `http://localhost:8081`
2. Create or use test account:
   - Email: `testuser@example.com`
   - Password: `TestPassword123!`
3. Click **Login** button
4. You should see the app home screen

**Expected Result:** ✅ Logged in, home screen visible

**Log Check:**
```
INFO: POST /api/v1/auth/login
INFO: User {user_id} logged in successfully
```

#### 2.2 Navigate to Conversation Screen

1. Click on **Conversation** tab (or "Start Conversation" button)
2. You should see conversation screen with:
   - Start Conversation button
   - Microphone icon
   - Status indicator

**Expected Result:** ✅ Conversation screen visible, Start button enabled

#### 2.3 Start Conversation Flow

**Record Timestamp 1 (Connection Start):** `_______:_______:_______` (HH:MM:SS.mmm)

1. Click **"Start Conversation"** button
2. If prompted, grant microphone permission
3. Watch for connection status to change to "Connected"
4. Monitor backend logs for bot joining

**Expected Result:**
- ✅ Microphone permission requested
- ✅ Status changes to "Connected" or "Ready"
- ✅ Backend logs show bot joined room

**Backend Logs to Check:**
```
INFO: Creating conversation {conversation_id}
INFO: Created Daily.co room: {room_name}
INFO: Spawning Pipecat bot
INFO: Bot joined room
```

**Timestamp Recording (AC1):**
- Start time: `_______:_______:_______`
- Connected time: `_______:_______:_______`
- **Connection latency (should be <3s):** `_______ seconds`

#### 2.4 Execute Speech Test

**Record Timestamp 2 (Speech Start):** `_______:_______:_______` (HH:MM:SS.mmm)

1. Speak clearly: **"Hello, can you hear me?"**
2. Wait for AI to respond (should hear voice within 5 seconds)
3. Listen to full response

**Expected Result:**
- ✅ Deepgram transcribes your speech
- ✅ Azure OpenAI generates a greeting response
- ✅ ElevenLabs synthesizes audio
- ✅ You hear AI voice in the app

**Record Timestamp 3 (Audio Start):** `_______:_______:_______` (when you hear AI response)

**Backend Logs to Check:**
```
[STT] Transcription: "Hello, can you hear me?"
[LLM] Response: "{AI response text}"
[TTS] Audio generated
```

**Performance Measurements (AC2, AC3, AC4, AC6):**
- Speech start time: `_______:_______:_______`
- Transcription in logs: `_______:_______:_______` → **STT latency: _______ ms** (should be <500ms)
- LLM response in logs: `_______:_______:_______` → **LLM latency: _______ ms** (should be <2s)
- TTS complete in logs: `_______:_______:_______` → **TTS latency: _______ ms** (should be <1s)
- Audio playback starts: `_______:_______:_______` → **Round-trip latency: _______ seconds** (should be <5s)

#### 2.5 End Conversation Flow

**Record Timestamp 4 (End Start):** `_______:_______:_______`

1. Click **"End Conversation"** button
2. Wait for connection to close
3. Verify UI returns to ready state
4. Monitor Daily.co dashboard - room should be deleted

**Expected Result:**
- ✅ Connection closes cleanly
- ✅ UI returns to "Start Conversation" ready state
- ✅ Backend logs show conversation ended
- ✅ Daily.co dashboard shows room deleted

**Backend Logs to Check:**
```
INFO: Attempting to end conversation {conversation_id}
INFO: Conversation {conversation_id} ended successfully. Duration: {seconds} seconds
INFO: Successfully deleted Daily.co room: {room_name}
```

#### 2.6 Verify Backend Logs

In the backend terminal, review logs and record:

**STT Logs:**
- Transcription text: `_______________________________`
- Transcription accuracy: ✅ Correct / ⚠️ Partial / ❌ Incorrect
- Latency measurement: `_______ ms`

**LLM Logs:**
- Received text: `_______________________________`
- Response generated: `_______________________________`
- Latency measurement: `_______ ms`

**TTS Logs:**
- Input text: `_______________________________`
- Audio generated: ✅ Yes / ❌ No
- Latency measurement: `_______ ms`

**Errors/Warnings:**
```
[Copy any error messages or warnings here]
_________________________________________________________________
_________________________________________________________________
```

#### 2.7 Verify Database Record

```bash
# Terminal 3: Query conversation table
cd /Users/hieutt50/projects/numerologist-ai/backend

psql -U postgres -d numerologist_ai << EOF
SELECT
  id,
  user_id,
  started_at,
  ended_at,
  duration_seconds,
  daily_room_id
FROM conversation
ORDER BY created_at DESC
LIMIT 1;
EOF
```

**Expected Output:**
```
                   id                   |                user_id                 |     started_at      |      ended_at       | duration_seconds |     daily_room_id
----------------------------------------+----------------------------------------+---------------------+---------------------+------------------+-------------------
 {conversation_uuid} | {user_uuid} | 2025-11-10 14:00:00 | 2025-11-10 14:05:00 |               300 | numerologist-ai-...
```

**Database Verification (AC10):**
- ✅ Conversation ID exists: `_______________________________`
- ✅ User ID matches: `_______________________________`
- ✅ Started at: `_______:_______:_______`
- ✅ Ended at: `_______:_______:_______`
- ✅ Duration seconds: `_______`
- ✅ Daily room ID: `_______________________________`

---

### Task 3: Performance & Latency Measurement

Create a summary of latency measurements from the test:

| Component | Start Time | End Time | Latency | Target | Status |
|-----------|-----------|----------|---------|--------|--------|
| Connection | `__:__:__` | `__:__:__` | `___ s` | <3s | ✅/❌ |
| STT | `__:__:__` | `__:__:__` | `___ ms` | <500ms | ✅/❌ |
| LLM | `__:__:__` | `__:__:__` | `___ ms` | <2s | ✅/❌ |
| TTS | `__:__:__` | `__:__:__` | `___ ms` | <1s | ✅/❌ |
| **Round-Trip Total** | `__:__:__` | `__:__:__` | `___ s` | <5s | ✅/❌ |

**Performance Analysis:**
- Overall MVP latency requirement (<5s): ✅ PASS / ❌ FAIL
- If >5s, identify bottleneck: `_______________________________`
- Optimization opportunities: `_______________________________`

---

### Task 4: Multi-Platform Testing

Test on additional platforms if available:

#### Chrome Browser (Baseline - Already Done Above)
- ✅ Test completed
- Audio quality: ✅ Good / ⚠️ Fair / ❌ Poor
- Latency: `___ seconds`

#### Safari Browser
```bash
# If available, test in Safari
# Open http://localhost:8081 in Safari and repeat conversation test
```
- ✅ Test completed / ❌ Skipped (Safari unavailable)
- Audio quality: ✅ Good / ⚠️ Fair / ❌ Poor
- Latency: `___ seconds`
- Issues: `_______________________________`

#### iOS Device/Simulator
```bash
# Build iOS app
cd /Users/hieutt50/projects/numerologist-ai/mobile
npm run ios

# Or test on real device if available
```
- ✅ Test completed / ❌ Skipped (iOS unavailable)
- Audio quality: ✅ Good / ⚠️ Fair / ❌ Poor
- Latency: `___ seconds`
- Issues: `_______________________________`

#### Android Device/Emulator
```bash
# Build Android app
cd /Users/hieutt50/projects/numerologist-ai/mobile
npm run android

# Or test on real device if available
```
- ✅ Test completed / ❌ Skipped (Android unavailable)
- Audio quality: ✅ Good / ⚠️ Fair / ❌ Poor
- Latency: `___ seconds`
- Issues: `_______________________________`

---

### Task 5: Error Scenario Testing

#### 5.1 Test Without Microphone Permission

1. Go to browser/app settings and **deny** microphone permission
2. Try to start conversation
3. Record result

**Expected:** App shows error message, conversation doesn't start

**Result:**
- ✅ Error message displayed: `_______________________________`
- ✅ Conversation didn't start: Yes / No
- Backend logs show error: Yes / No
- Error message was user-friendly: Yes / No

**Backend Logs Check:**
```
[Copy error logs here]
_________________________________________________________________
```

#### 5.2 Test Network Interruption

1. Start a conversation normally
2. Speak a phrase to initiate voice pipeline
3. Simulate network interruption (disconnect WiFi or throttle network)
4. Record result

**Expected:** Graceful error handling, user sees error message

**Result:**
- ✅ Error handled gracefully: Yes / No
- ✅ No crash or freeze: Yes / No
- ✅ User-friendly error message: Yes / No
- Error message: `_______________________________`

#### 5.3 Test Invalid API Key

1. Edit backend `.env` file - temporarily break one API key (e.g., change DEEPGRAM_API_KEY)
2. Restart backend server
3. Try to start conversation and speak
4. Record result
5. **Fix API key and restart backend**

**Expected:** API error is logged, user sees appropriate error

**Result:**
- ✅ Error logged in backend: Yes / No
- ✅ User sees error message: Yes / No
- Error message: `_______________________________`
- Backend logs: `_______________________________`

#### 5.4 Test Multiple Start/End Cycles

1. Run 3 consecutive conversation cycles:
   - Start conversation
   - Speak briefly
   - End conversation
   - Repeat

**Expected:** No memory leaks, state resets correctly

**Results:**

**Cycle 1:**
- Started: ✅ / ❌
- Conversation worked: ✅ / ❌
- Ended cleanly: ✅ / ❌

**Cycle 2:**
- Started: ✅ / ❌
- Conversation worked: ✅ / ❌
- Ended cleanly: ✅ / ❌

**Cycle 3:**
- Started: ✅ / ❌
- Conversation worked: ✅ / ❌
- Ended cleanly: ✅ / ❌

**Memory/State Check:**
- App UI responsive: ✅ Yes / ❌ No
- No stale data visible: ✅ Yes / ❌ No
- Backend logs clean (no orphaned processes): ✅ Yes / ❌ No

---

### Task 6: Documentation & Reporting

#### 6.1 Summary of Test Results

**Date Tested:** `_______________________________`
**Tester:** `_______________________________`
**Platform(s) Tested:** `_______________________________`

**Acceptance Criteria Summary:**

- [ ] AC1: Conversation Start Flow - ✅ PASS / ❌ FAIL
- [ ] AC2: Speech Recognition (STT) - ✅ PASS / ❌ FAIL
- [ ] AC3: LLM Response Generation - ✅ PASS / ❌ FAIL
- [ ] AC4: Speech Synthesis (TTS) - ✅ PASS / ❌ FAIL
- [ ] AC5: Audio Playback - ✅ PASS / ❌ FAIL
- [ ] AC6: Round-Trip Performance - ✅ PASS / ❌ FAIL
- [ ] AC7: Conversation End Flow - ✅ PASS / ❌ FAIL
- [ ] AC8: Backend Logging & Monitoring - ✅ PASS / ❌ FAIL
- [ ] AC9: Device Testing - ✅ PASS / ❌ FAIL
- [ ] AC10: Data Persistence - ✅ PASS / ❌ FAIL

**Overall Status:** 🟢 ALL PASS / 🟡 PARTIAL / 🔴 FAILURES

#### 6.2 Known Issues & Workarounds

```
Issue #1:
Description: _________________________________________________________________
Severity: 🔴 High / 🟡 Medium / 🟢 Low
Workaround: _________________________________________________________________

Issue #2:
Description: _________________________________________________________________
Severity: 🔴 High / 🟡 Medium / 🟢 Low
Workaround: _________________________________________________________________
```

#### 6.3 Captured Evidence

**Backend Logs Captured:**
```
[Paste relevant log snippets here, including timestamps]
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
```

**Screenshots/Recordings:**
- Start conversation flow: Yes / No
- Speech test in progress: Yes / No
- End conversation: Yes / No
- Daily.co dashboard room: Yes / No
- Database query result: Yes / No

---

## Result Recording Template

Use this template to summarize all test results:

```markdown
# Story 3.10 Test Results

**Date:** [DATE]
**Tester:** [NAME]
**Environment:** [Chrome/Safari/iOS/Android]

## Acceptance Criteria Results

### AC1: Conversation Start Flow
- [ ] User can tap "Start Conversation" button
- [ ] App requests microphone permission
- [ ] App joins Daily.co room
- [ ] Backend logs show bot joined
- [ ] Connection <3 seconds: ✅ [__s] / ❌

### AC2: Speech Recognition (STT)
- [ ] Speech transcribed correctly: "Hello, can you hear me?"
- [ ] Backend logs show transcription
- [ ] Latency <500ms: ✅ [__ms] / ❌

### AC3: LLM Response Generation
- [ ] LLM generates response
- [ ] Backend logs show LLM output
- [ ] Latency <2s: ✅ [__ms] / ❌

### AC4: Speech Synthesis (TTS)
- [ ] TTS generates audio
- [ ] Backend logs show success
- [ ] Latency <1s: ✅ [__ms] / ❌

### AC5: Audio Playback
- [ ] User hears AI response
- [ ] Audio quality clear
- [ ] No glitches/stuttering

### AC6: Round-Trip Performance
- [ ] Total latency <5s: ✅ [__s] / ❌
- [ ] Measured start-to-playback time
- [ ] Baseline established

### AC7: Conversation End Flow
- [ ] End button works
- [ ] Conversation ends cleanly
- [ ] Backend updates record
- [ ] Room deleted from Daily.co
- [ ] UI returns to ready state

### AC8: Backend Logging & Monitoring
- [ ] All events logged with timestamps
- [ ] Errors logged with context
- [ ] Daily.co dashboard shows activity
- [ ] All API keys working

### AC9: Device Testing
- [ ] Web (Chrome): ✅ / ❌
- [ ] Web (Safari): ✅ / ❌ / N/A
- [ ] iOS: ✅ / ❌ / N/A
- [ ] Android: ✅ / ❌ / N/A
- [ ] Platform issues documented

### AC10: Data Persistence
- [ ] Conversation saved to database
- [ ] All required fields set
- [ ] Daily room ID stored
- [ ] Data retrievable

## Summary

**Overall Result:** 🟢 PASS / 🟡 PARTIAL / 🔴 FAIL

**Issues Found:**
[List any issues]

**Performance Baseline:**
- Average round-trip latency: [__s]
- Bottleneck (if any): [component]

**Recommendations:**
[Any observations for Epic 6 optimization]
```

---

## Troubleshooting

### Backend Server Issues

**Problem:** Backend server won't start
```bash
# Check for port conflicts
lsof -i :8000

# Kill any process on port 8000
kill -9 <PID>

# Try restarting
uv run uvicorn src.main:app --reload --port 8001
```

**Problem:** Database connection error
```bash
# Verify PostgreSQL is running
psql -U postgres -d numerologist_ai -c "SELECT 1"

# Run migrations
cd backend && uv run alembic upgrade head
```

### Frontend Issues

**Problem:** Frontend won't connect to backend
```bash
# Check backend is running on port 8000
curl http://localhost:8000/health

# Frontend should connect to http://localhost:8000 (check API_URL env var)
```

**Problem:** Microphone not working
- Check browser permissions for microphone
- Test microphone in browser settings
- Ensure Expo/React Native has microphone access

### Voice Pipeline Issues

**Problem:** No transcription (STT not working)
- Verify DEEPGRAM_API_KEY in .env
- Check backend logs for Deepgram errors
- Test Deepgram API directly: `curl -H "Authorization: Token $DEEPGRAM_API_KEY" https://api.deepgram.com/v1/status`

**Problem:** LLM not responding
- Verify AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT in .env
- Check Azure OpenAI quota hasn't been exceeded
- Review backend logs for OpenAI errors

**Problem:** No audio output (TTS not working)
- Verify ELEVENLABS_API_KEY in .env
- Check ElevenLabs API status
- Verify app speaker permissions

---

**Ready to test!** Follow the tasks above and record all results in the template. When complete, update the story file with results and mark acceptance criteria as passing.

