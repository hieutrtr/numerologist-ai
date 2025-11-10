# daily-react vs daily-js Analysis for Story 3.8

**Date:** 2025-11-10
**Context:** Evaluating SDK choices for voice integration
**Project:** Numerologist AI (React Native + Expo + Node backend)

---

## 🎯 Executive Summary

**Short Answer:**
- ❌ **Cannot use daily-react for Story 3.8** (mobile app)
- ✅ **Current choice (daily-js + react-native-daily-js) is correct**
- ⚠️ **Combination approach doesn't apply to this architecture**

---

## 📊 Comparison Matrix

| Aspect | daily-js | daily-react | react-native-daily-js |
|--------|----------|-------------|----------------------|
| **Platform** | Web only | Web + React | Mobile only |
| **Framework** | Vanilla JS | React hooks | React Native |
| **Use Case** | Browser apps | React web apps | Mobile (iOS/Android) |
| **State Mgmt** | Manual or external | Jotai built-in | Manual or external |
| **Expo Support** | ✅ Yes (web) | ✅ Yes (web) | ⚠️ Limited (needs plugin) |
| **Story 3.8 Use** | ❌ No | ❌ No | ✅ Yes (correct choice) |

---

## 📚 What Each Library Does

### 1. daily-js (`@daily-co/daily-js`)

**Purpose:** Low-level WebRTC JavaScript library for web browsers

**What it is:**
- Core Daily.co SDK for web
- Raw API access to call object
- Requires manual state management
- No UI components included

**Best for:**
- Custom web applications
- Browser-based video/audio apps
- When you need full control

**Example:**
```typescript
// daily-js (what we use for Expo Web)
const call = await DailyIframe.createCallObject({
  audioSource: true,
  videoSource: false
});
await call.join({ url, token });
```

### 2. daily-react (`@daily-co/daily-react`)

**Purpose:** React hooks wrapper around daily-js for web applications

**What it is:**
- Higher-level abstraction of daily-js
- React hooks: useCallObject, useDailyEvent, etc.
- Built-in state management via Jotai
- Designed for React web apps

**Dependencies:**
- Requires: `@daily-co/daily-js` + `jotai`
- Built ON TOP of daily-js

**Best for:**
- React web applications
- Teams using React hooks
- Reduced boilerplate code

**Example:**
```typescript
// daily-react (for web React apps)
const { callObject } = useCallObject();
const [callState, setCallState] = useState('idle');

useDailyEvent('joined-meeting', () => {
  setCallState('joined');
});

// Much higher level than daily-js
```

### 3. react-native-daily-js (`@daily-co/react-native-daily-js`)

**Purpose:** Native Daily.co SDK for React Native mobile apps

**What it is:**
- Native module for iOS and Android
- Similar API to daily-js but optimized for mobile
- Direct native WebRTC implementation
- No React hooks wrapper

**Best for:**
- React Native applications
- iOS and Android apps
- Expo apps (with config plugin or ejection)

**Example:**
```typescript
// react-native-daily-js (what we use for Story 3.8)
const call = await DailyIframe.createCallObject({
  audioSource: true,
  videoSource: false
});
await call.join({ url, token });
// Same API as daily-js but native implementation
```

---

## 🏗️ Architecture Decision for Your Project

### Current Setup ✅ (CORRECT)

```
┌─────────────────────────────────────┐
│ numerologist-ai (Backend + Frontend)│
└─────────┬───────────────────────────┘
          │
    ┌─────┴──────┐
    │            │
    ▼            ▼
┌────────┐    ┌──────────────┐
│ Mobile │    │ Web (Future) │
│(Expo)  │    │              │
└───┬────┘    └──────┬───────┘
    │                │
    ▼                ▼
┌─────────────┐  ┌─────────────┐
│ react-native│  │ daily-react │
│ -daily-js   │  │ (future)    │
└─────────────┘  └─────────────┘
```

### Your Use Case Now

**Story 3.8: Mobile Voice Integration**

```
Story 3.8 (Mobile)
    ↓
React Native + Expo
    ↓
react-native-daily-js ✅ (CORRECT)
    │
    ├─ Android: Native WebRTC
    ├─ iOS: Native WebRTC
    └─ Expo Web: Platform detection uses daily-js
```

**File: mobile/src/services/daily.service.ts**

```typescript
// Platform detection at runtime
const isNativeEnvironment = (): boolean => {
  try {
    return Platform.OS !== 'web';
  } catch {
    return false;
  }
};

if (isNativeEnvironment()) {
  // Mobile (Android/iOS)
  DailyIframe = require('@daily-co/react-native-daily-js');
} else {
  // Web (Expo Web)
  DailyIframe = require('@daily-co/daily-js');
}
```

This is **optimal** because:
- Uses native SDK for native performance
- Falls back to web SDK for Expo Web
- Single codebase for all platforms
- No daily-react overhead needed

---

## ❌ Why daily-react Won't Work for Story 3.8

### Limitation 1: Web-Only Framework

daily-react is **exclusively for React web applications**

```typescript
// ❌ This WON'T work in React Native
import { useCallObject } from '@daily-co/daily-react';

// Error: Cannot use web hooks in React Native environment
// React hooks are web-specific
```

### Limitation 2: No React Native Support

daily-react requires:
- React DOM (web only)
- Browser APIs
- Jotai (state management)

**None of these exist in React Native**

### Limitation 3: Dependencies Incompatibility

```json
{
  "dependencies": {
    "@daily-co/daily-react": "^0.x",
    "react-dom": "web-only",  // ❌ Not in React Native
    "jotai": "web-focused"     // ❌ Different state mgmt model
  }
}
```

---

## 🤔 Could We Use a Combination?

**Short Answer: No, it doesn't apply here.**

**Why not:**

1. **Different Targets**
   - daily-react: for web (React)
   - react-native-daily-js: for mobile (React Native)
   - They serve completely different platforms

2. **No Shared Code**
   - Web React and React Native don't share UI code
   - Different navigation, components, state management
   - Would require duplicate implementations

3. **Unnecessary Complexity**
   - daily.service.ts is already a perfect abstraction layer
   - Works for both web and mobile via platform detection
   - Adding daily-react would just complicate things

### What a "Combination" Would Look Like (NOT RECOMMENDED)

```
❌ BAD APPROACH:
├─ Mobile: react-native-daily-js
├─ Web: daily-react (different hooks, different state)
└─ Backend integration logic: Duplicated or shared?
   → Complexity increases, no real benefit

✅ CURRENT APPROACH (RECOMMENDED):
├─ Mobile: react-native-daily-js
├─ Web: daily-js (lightweight, same service layer)
└─ Backend integration: daily.service.ts (single abstraction)
   → Simple, consistent, maintainable
```

---

## 🎯 Scenarios Where daily-react Would Be Useful

### If You Built a Web Version Later

Suppose you want to add a web app alongside the mobile app:

```
Numerologist AI Project
├─ Mobile App (Story 3.8) ✅
│  ├─ React Native
│  ├─ react-native-daily-js
│  └─ Expo
│
└─ Web App (Future)
   ├─ React (Next.js/React.js)
   ├─ daily-react ← Would make sense here
   └─ Browser
```

**Then daily-react would be valuable:**
- React web app gets React hooks
- Better DX with useCallObject, useDailyEvent
- Jotai for state management
- No need for custom service layer

**But current architecture is fine:**
- daily.service.ts works for both
- Expo Web uses daily-js platform detection
- Consistent API across platforms

---

## 📊 Decision Matrix

| Question | Answer | Reason |
|----------|--------|--------|
| **Use daily-react for Story 3.8?** | ❌ No | Web-only, won't work in React Native |
| **Use daily-js for Story 3.8?** | ✅ Yes (indirectly) | Via daily.service.ts + platform detection |
| **Use react-native-daily-js for Story 3.8?** | ✅ Yes (primary) | Native mobile implementation |
| **Combine daily-react + daily-js?** | ❌ No | Architecture doesn't support it; different platforms |
| **Combine daily-react + react-native-daily-js?** | ❌ No | Different platforms; would require code duplication |
| **Keep current setup?** | ✅ Yes (best) | Single abstraction, platform detection, optimal |

---

## ✅ Current Implementation: OPTIMAL

Your current `daily.service.ts` approach is actually the **best practice** because:

1. **Abstraction Layer** - daily.service.ts encapsulates all Daily.co logic
2. **Platform Agnostic** - Same service works for Android, iOS, Web
3. **Runtime Detection** - Chooses correct SDK based on environment
4. **No Duplication** - Single code path for all platforms
5. **Zero Overhead** - No extra dependencies or state management layers
6. **Production Ready** - Tested, verified, working

### Architecture

```typescript
// Single abstraction layer
daily.service.ts
├─ Platform detection (web vs native)
├─ SDK selection (daily-js vs react-native-daily-js)
└─ Consistent API for all platforms
    │
    ├─ Android: react-native-daily-js
    ├─ iOS: react-native-daily-js
    └─ Web: daily-js
```

---

## 🚀 Recommendations

### For Story 3.8 (Current)
✅ **Keep current approach**
- Use `daily.service.ts` abstraction
- Platform detection for SDK selection
- No changes needed to daily-react

### For Future Web Version (if built)
✅ **Then consider daily-react**
- Create separate web app
- Use daily-react in web React components
- Keep daily.service.ts for mobile
- Share backend integration only

### For Future Hybrid Sharing
If you later want to share more code between web and mobile:
- Keep daily.service.ts for mobile
- Create separate daily-react service for web
- Share business logic, not Daily.co integration
- They have different SDKs, different state models

---

## 📝 Conclusion

### Question: "Can we use daily-react instead of daily-js?"

**Answer:**
- ❌ No, daily-react is for React web apps only
- ✅ Your current setup with daily-js + react-native-daily-js is correct
- ✅ daily.service.ts abstraction layer is optimal
- ✅ Platform detection handles both mobile and web

### Question: "Or use combination of them?"

**Answer:**
- ❌ Combination doesn't apply to this architecture
- ❌ Would add unnecessary complexity
- ✅ Current single-abstraction approach is superior
- ✅ Keep daily.service.ts as is for Story 3.8

### Status: Story 3.8

✅ **Architecture is OPTIMAL**
✅ **SDK choices are CORRECT**
✅ **Implementation is PRODUCTION READY**
✅ **No changes recommended**

---

## 📖 Reference

| Library | Purpose | Best For | Story 3.8 |
|---------|---------|----------|-----------|
| **daily-js** | Web JavaScript SDK | Browser apps | ✅ Used (Expo Web fallback) |
| **daily-react** | React hooks wrapper | React web apps | ❌ Not applicable (web-only) |
| **react-native-daily-js** | Mobile native SDK | React Native apps | ✅ Used (primary, mobile) |
| **daily.service.ts** | Abstraction layer | All platforms | ✅ Perfect abstraction |

**Your choice is production-grade. No changes needed.** ✅
