# Daily.co Service Usage Guide - How It Works Right Now

**Created:** 2025-11-10
**Story:** 3.8 - Daily.co React Native Integration
**Status:** REVIEW - ACTIVE & USED

---

## 🎯 Quick Answer: Where Is daily.service Being Used?

**Daily.co service is CURRENTLY BEING USED in three places:**

### 1️⃣ **Story 3.5: Zustand Store** (useConversationStore.ts)
   - Imports: `import * as dailyService from '../services/daily.service'`
   - Calls in `startConversation()`: Initialize → Setup Listeners → Join Room
   - Calls in `endConversation()`: Teardown call and cleanup

### 2️⃣ **Story 3.7: Conversation Screen UI** (ConversationScreen component)
   - Uses the store which uses daily.service
   - User taps Start button → Store calls daily.service → WebRTC connects
   - UI shows connected state, displays error messages from daily.service

### 3️⃣ **Story 3.8: Test Suite** (daily.service.test.ts)
   - 45+ test cases covering all 7 daily.service functions
   - Tests all acceptance criteria
   - Ready to run once jest is configured

---

## 📍 The Exact Flow: What Happens Step-by-Step

### **When User Taps "Start Conversation" Button:**

```
┌─────────────────────────────────────────────────────────────┐
│ 1. USER INTERFACE (Story 3.7)                               │
│    ConversationScreen.tsx line 93                           │
│    User taps green microphone button                        │
└──────────────┬────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. PERMISSION CHECK (Story 3.6)                             │
│    audio.service.ts                                         │
│    ├─ checkMicrophonePermission()                           │
│    └─ requestMicrophonePermission() if needed               │
└──────────────┬────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. CALL STORE ACTION (Story 3.5)                            │
│    useConversationStore.startConversation()                 │
│    Line: useConversationStore.ts:100-222                    │
│                                                              │
│    STEP 1: Get room credentials from backend                │
│    ├─ await apiClient.post('/api/v1/conversations/start')   │
│    ├─ Backend: Story 3.4 creates room (Story 3.2)          │
│    ├─ Backend: Bot prepares response (Story 3.3)           │
│    └─ Returns: {conversation_id, daily_room_url,           │
│                 daily_token}                               │
└──────────────┬────────────────────────────────────────────┘
               │
               ├─────────────────────────────────┐
               │ STEP 2: INITIALIZE CALL         │
               │ daily.service.ts line 79        │
               ▼                                 ▼
        ┌────────────────────────────────────────────────────┐
        │ await dailyService.initializeCall()                │
        │                                                     │
        │ Function: daily.service.ts lines 79-112            │
        │                                                     │
        │ What it does:                                      │
        │ 1. Import @daily-co/react-native-daily-js SDK     │
        │ 2. Create call object with config:                │
        │    {                                               │
        │      videoSource: false,  (audio only)             │
        │      audioSource: true,   (enable mic)             │
        │      audioOutput: true    (enable speaker)         │
        │    }                                               │
        │ 3. Validate call object was created               │
        │ 4. Return call object reference                    │
        │                                                     │
        │ Returns: DailyCallObject (WebRTC connection)       │
        │ Throws: Error if initialization fails              │
        └───────────────┬────────────────────────────────────┘
                        │
                        ├─────────────────────────────────┐
                        │ STEP 3: SETUP LISTENERS         │
                        │ daily.service.ts line 258       │
                        ▼                                 ▼
        ┌────────────────────────────────────────────────────┐
        │ cleanupListeners =                                 │
        │   dailyService.setupCallListeners(                │
        │     callObject,                                    │
        │     {                                              │
        │       onConnected: callback,                       │
        │       onDisconnected: callback,                    │
        │       onError: callback,                           │
        │       onParticipantJoined: callback,               │
        │       onParticipantLeft: callback,                 │
        │       onNetworkQuality: callback                   │
        │     }                                              │
        │   )                                                │
        │                                                     │
        │ Function: daily.service.ts lines 258-376           │
        │                                                     │
        │ What it does:                                      │
        │ 1. For EACH callback provided:                     │
        │    ├─ Create handler wrapper                       │
        │    ├─ Add debug logging                            │
        │    ├─ Register with: call.on('event', handler)    │
        │    └─ Track handler for cleanup                    │
        │                                                     │
        │ 2. Maps 6 Daily.co events:                         │
        │    ├─ 'joined-meeting' → onConnected              │
        │    ├─ 'left-meeting' → onDisconnected             │
        │    ├─ 'error' → onError                           │
        │    ├─ 'participant-joined' → onParticipantJoined  │
        │    ├─ 'participant-left' → onParticipantLeft      │
        │    └─ 'network-quality-change' → onNetworkQuality │
        │                                                     │
        │ 3. Return cleanup function for later use           │
        │    cleanup() removes all listeners                 │
        │                                                     │
        │ Returns: cleanup function                          │
        │ Stored in: cleanupListeners variable              │
        └───────────────┬────────────────────────────────────┘
                        │
                        ├─────────────────────────────────┐
                        │ STEP 4: JOIN ROOM               │
                        │ daily.service.ts line 188       │
                        ▼                                 ▼
        ┌────────────────────────────────────────────────────┐
        │ await dailyService.joinRoom(callObject, {         │
        │   roomUrl: daily_room_url,                         │
        │   token: daily_token                              │
        │ })                                                 │
        │                                                     │
        │ Function: daily.service.ts lines 188-247           │
        │                                                     │
        │ What it does:                                      │
        │ 1. Validate room URL format                       │
        │    └─ must start with 'http'                      │
        │                                                     │
        │ 2. Configure audio (calls configureAudio)         │
        │    ├─ call.setAudioInputEnabled(true)             │
        │    ├─ call.setAudioOutputEnabled(true)            │
        │    └─ Platform-specific routing (Android/iOS)     │
        │                                                     │
        │ 3. Join Daily.co room                             │
        │    └─ await call.join({                           │
        │        url: roomUrl,                              │
        │        token: token                               │
        │      })                                           │
        │      ✅ WEBRTC CONNECTION ESTABLISHED!            │
        │                                                     │
        │ 4. Map errors to user-friendly messages           │
        │    ├─ Network → "Network error - check..."        │
        │    ├─ Permission → "Permission denied..."         │
        │    └─ Room expired → "Room no longer available..." │
        │                                                     │
        │ Returns: void (connection established)             │
        │ Throws: Error with user-friendly message          │
        └───────────────┬────────────────────────────────────┘
                        │
                        ├─────────────────────────────────┐
                        │ STEP 5: UPDATE STORE STATE      │
                        │ useConversationStore.ts line 183│
                        ▼                                 ▼
        ┌────────────────────────────────────────────────────┐
        │ set({                                              │
        │   conversationId: conversation_id,                 │
        │   dailyCall: callObject,    ← Daily.co reference  │
        │   isConnected: true,        ← Trigger UI update   │
        │   isMicActive: true,                              │
        │   error: null                                      │
        │ })                                                 │
        │                                                     │
        │ Zustand subscribers notified of state change      │
        └───────────────┬────────────────────────────────────┘
                        │
                        ▼
               ┌────────────────────┐
               │ Daily.co fires      │
               │'joined-meeting'     │
               │event                │
               └────────┬───────────┘
                        │
                        ▼
               ┌────────────────────┐
               │ Handler executes:   │
               │ console.log()       │
               │ onConnected()       │
               │ set({isConnected})  │
               └────────┬───────────┘
                        │
                        ▼
               ┌────────────────────┐
               │ Zustand notifies    │
               │ subscribers         │
               └────────┬───────────┘
                        │
                        ▼
        ┌─────────────────────────────────────────────────────┐
        │ 4. UI RE-RENDERS (Story 3.7)                        │
        │    ConversationScreen component re-renders         │
        │                                                      │
        │    UI NOW SHOWS:                                    │
        │    ✅ Button text: "End"                            │
        │    ✅ Button color: Cyan/Active                     │
        │    ✅ Status: "Connected - Speak now"               │
        │    ✅ Microphone icon: Pulsing animation            │
        │    ✅ No error message                              │
        └────────────────────────────────────────────────────┘
                        │
                        ▼
                  🎙️ CONVERSATION READY
                  User can speak to bot
                  Bot can respond in real-time
```

---

## 📊 Data Flow: Store State to UI

```
Daily.co Events
    ↓
Handler executes
    ├─ onConnected()
    ├─ onError()
    ├─ onParticipantJoined()
    └─ etc.
    ↓
Store callbacks run:
    └─ set({ isConnected: true, error: null })
    ↓
Zustand state updated:
    ├─ conversationId: "abc-123"
    ├─ dailyCall: DailyCallObject
    ├─ isConnected: true
    ├─ isMicActive: true
    ├─ isAISpeaking: false
    └─ error: null
    ↓
Zustand notifies subscribers
    ↓
ConversationScreen subscribed
    └─ const { isConnected } = useConversationStore()
    ↓
Component re-renders with new state
    ↓
UI shows:
    ├─ "End" button (because isConnected = true)
    ├─ Active button styling
    ├─ Pulsing animation
    └─ "Connected - Speak now" status
```

---

## 🔌 Current Integration Points

### **Integration 1: Backend (Story 3.4)**

```
User Start Request
    ↓
Store calls: apiClient.post('/api/v1/conversations/start')
    ↓
Backend (Story 3.4) endpoint:
    ├─ Creates Daily.co room (Story 3.2)
    ├─ Initializes bot (Story 3.3)
    └─ Returns: {
         conversation_id: "conv-123",
         daily_room_url: "https://example.daily.co/abc",
         daily_token: "eyJ0eXAi..."
       }
    ↓
Store passes room_url + token to:
    └─ dailyService.joinRoom(callObject, {roomUrl, token})
```

### **Integration 2: Zustand Store (Story 3.5)**

```
store.startConversation() calls:
    ├─ dailyService.initializeCall()
    ├─ dailyService.setupCallListeners(callObject, {
    │    onConnected: () => set({ isConnected: true })
    │    onError: (msg) => set({ error: msg })
    │  })
    └─ dailyService.joinRoom(callObject, credentials)

store.endConversation() calls:
    └─ dailyService.teardownCall(dailyCall, cleanupListeners)
```

### **Integration 3: Permissions (Story 3.6)**

```
ConversationScreen.handlePress() calls:
    ├─ checkMicrophonePermission()  ← Story 3.6
    ├─ requestMicrophonePermission()← Story 3.6
    └─ if (hasPermission)
       └─ startConversation()
          └─ dailyService starts connection
             └─ If error: "Microphone permission denied"
```

### **Integration 4: UI Component (Story 3.7)**

```
ConversationScreen subscribes to store:
    const { isConnected, error } = useConversationStore()

    ↓

When dailyService events fire:
    ├─ onConnected fires
    ├─ Store updates: set({ isConnected: true })
    ├─ Zustand notifies subscribers
    ├─ Component re-renders
    └─ UI shows "End" button + pulsing animation
```

---

## 🛠️ What Each daily.service Function Does (Currently Used)

### **1. initializeCall()** - Lines 79-112
**Called by:** `useConversationStore.startConversation()` line 124

**Purpose:** Create Daily.co call object with audio configuration

**Current usage:**
```typescript
const callObject = await dailyService.initializeCall();
```

**What happens:**
- Imports Daily.co SDK
- Creates call object with: videoSource: false, audioSource: true
- Validates object was created
- Returns reference for later use

**Error handling:** Throws error if creation fails

---

### **2. setupCallListeners()** - Lines 258-376
**Called by:** `useConversationStore.startConversation()` line 127

**Purpose:** Wire Daily.co events to store update callbacks

**Current usage:**
```typescript
cleanupListeners = dailyService.setupCallListeners(callObject, {
  onConnected: () => set({ isConnected: true }),
  onDisconnected: () => set({ isConnected: false }),
  onError: (msg) => set({ error: msg }),
  // ... more callbacks
});
```

**What happens:**
- For EACH callback: Create wrapper with logging
- Register wrapper with Daily.co: `call.on('event', wrapper)`
- Return cleanup function for later removal

**Why important:** Loose coupling between daily.service and store

---

### **3. joinRoom()** - Lines 188-247
**Called by:** `useConversationStore.startConversation()` line 177

**Purpose:** Establish WebRTC connection to Daily.co room

**Current usage:**
```typescript
await dailyService.joinRoom(callObject, {
  roomUrl: daily_room_url,
  token: daily_token,
});
```

**What happens:**
1. Validate room URL format
2. Configure audio via `configureAudio()`
3. Join room with credentials: `await call.join({url, token})`
4. Map errors to user-friendly messages

**Error handling:** Throws with mapped error message

---

### **4. teardownCall()** - Lines 387-424
**Called by:** `useConversationStore.endConversation()` line 252

**Purpose:** Clean up Daily.co connection and free resources

**Currently used in:** Story 3.5 store (when user ends conversation)

**Will be used in:** Story 3.9 (end conversation endpoint)

**What happens:**
1. Remove all event listeners: `call.off(event, handler)`
2. Leave room gracefully: `await call.leave()`
3. Destroy call object: `call.destroy()`
4. Best-effort cleanup (doesn't throw)

---

### **5. configureAudio()** - Lines 123-174
**Called by:** `joinRoom()` line 210-214

**Purpose:** Configure microphone and speaker settings

**Current usage:** Automatic, called from joinRoom()

**What happens:**
1. Enable microphone: `call.setAudioInputEnabled(true)`
2. Enable speaker: `call.setAudioOutputEnabled(true)`
3. Platform-specific routing (Android prefers speaker)

---

### **6. getParticipants()** - Lines 434-460
**Current status:** Written but not yet called in active code

**Future usage:** Story 3.10 for participant tracking UI

---

### **7. isConnected()** - Lines 468-476
**Current status:** Written but not yet called (store uses isConnected state instead)

**Future usage:** Could be used for manual connection checks

---

## ⚙️ How Callbacks Are Currently Used

### **In useConversationStore.ts (lines 127-170)**

```typescript
cleanupListeners = dailyService.setupCallListeners(callObject, {
  // CALLBACK 1: When user joins room
  onConnected: () => {
    set({ isConnected: true, error: null });
    if (__DEV__) console.log('[Store] Update: connected');
  },

  // CALLBACK 2: When user leaves room
  onDisconnected: () => {
    set({ isConnected: false });
    if (__DEV__) console.log('[Store] Update: disconnected');
  },

  // CALLBACK 3: When error occurs
  onError: (errorMsg: string) => {
    let userMessage = errorMsg;
    if (errorMsg.includes('permission')) {
      userMessage = 'Microphone permission denied';
    } else if (errorMsg.includes('network')) {
      userMessage = 'Network error - check your connection';
    }
    set({ error: userMessage });
    if (__DEV__) console.log('[Store] Error:', userMessage);
  },

  // CALLBACK 4: When bot joins
  onParticipantJoined: (participant) => {
    if (__DEV__) {
      console.log('[Store] Participant joined:', participant.id);
    }
    // Future: track participants
  },

  // CALLBACK 5: When someone leaves
  onParticipantLeft: (participantId) => {
    if (__DEV__) console.log('[Store] Participant left:', participantId);
  },

  // CALLBACK 6: Network quality changes
  onNetworkQuality: (quality) => {
    if (__DEV__) console.log('[Store] Network quality:', quality);
    // Future: update network quality indicator
  },
});
```

---

## 🔄 When User Ends Conversation

```
User taps "End" button
    ↓
ConversationScreen.handlePress() (line 105-117)
    ├─ await endConversation()
    ↓
Store: endConversation() (line 241-300)
    ├─ STEP 1: dailyService.teardownCall()
    │  └─ cleanupListeners()
    │  ├─ call.leave()
    │  └─ call.destroy()
    │
    ├─ STEP 2: Backend notification (will be in Story 3.9)
    │  └─ await apiClient.post(`/api/v1/conversations/${id}/end`)
    │
    └─ STEP 3: Reset store state
       └─ set({ isConnected: false, dailyCall: null, ... })
           ↓
           Zustand notifies subscribers
           ↓
           UI re-renders
           ↓
           Shows "Start" button
           ↓
           Ready for next conversation
```

---

## 📝 Summary Table: What's Used and Where

| Function | Called From | Called In | Current Status |
|----------|------------|-----------|-----------------|
| `initializeCall()` | useConversationStore | startConversation | ✅ ACTIVE |
| `configureAudio()` | joinRoom | automatically | ✅ ACTIVE |
| `joinRoom()` | useConversationStore | startConversation | ✅ ACTIVE |
| `setupCallListeners()` | useConversationStore | startConversation | ✅ ACTIVE |
| `teardownCall()` | useConversationStore | endConversation | ✅ ACTIVE |
| `getParticipants()` | - | (not called yet) | ⏳ Future use |
| `isConnected()` | - | (not called yet) | ⏳ Future use |

---

## 🎯 In 1 Sentence

**Daily.co service is the bridge that connects the React Native mobile UI to Daily.co's WebRTC infrastructure, handling connection lifecycle, event management, and error mapping for voice conversations.**

