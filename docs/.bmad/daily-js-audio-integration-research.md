# Deep Research: How daily-js Handles Machine Audio Integration

**Date:** 2025-11-10
**Research Depth:** Comprehensive
**Focus:** Audio device management, configuration, and quality optimization

---

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Audio Input Management](#audio-input-management)
3. [Audio Output Management](#audio-output-management)
4. [Audio Quality Configuration](#audio-quality-configuration)
5. [Device Enumeration & Selection](#device-enumeration--selection)
6. [Best Practices](#best-practices)
7. [Implementation Guide for Story 3.8](#implementation-guide-for-story-38)

---

## 🏗️ Architecture Overview

### How daily-js Integrates with Machine Audio

```
┌─────────────────────────────────────────────────────┐
│ daily-js (JavaScript Library)                       │
└────────┬────────────────────────────────────────────┘
         │ Uses
         ▼
┌─────────────────────────────────────────────────────┐
│ WebRTC (Web Audio API + MediaDevices API)          │
└────────┬────────────────────────────────────────────┘
         │
    ┌────┴────┬──────────────┐
    ▼         ▼              ▼
┌────────┐ ┌──────────┐ ┌─────────────┐
│ Audio  │ │ Browser  │ │ OS Audio    │
│ Input  │ │ Audio    │ │ Hardware    │
│(Mic)   │ │ Context  │ │ (Speaker,   │
│        │ │          │ │  Mic)       │
└────────┘ └──────────┘ └─────────────┘
```

### Key Components

| Component | Purpose | Control Level |
|-----------|---------|----------------|
| **createCallObject()** | Create audio/video call instance | Initialization |
| **audioSource** | Enable/configure microphone input | At initialization |
| **setLocalAudio()** | Toggle microphone on/off | During call |
| **updateInputSettings()** | Apply audio constraints & effects | During call |
| **setInputDevicesAsync()** | Switch microphone device | Before/during call |
| **setOutputDeviceAsync()** | Switch speaker device | Before/during call |
| **enumerateDevices()** | List available devices | Query |

---

## 🎤 Audio Input Management

### 1. Initial Audio Source Configuration

**At createCallObject() time:**

```typescript
// Simple: Enable audio input
const call = await DailyIframe.createCallObject({
  audioSource: true,  // ✅ Enable microphone
  videoSource: false  // Disable camera
});

// Advanced: Use custom audio track
const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
const audioTrack = stream.getAudioTracks()[0];

const call = await DailyIframe.createCallObject({
  audioSource: audioTrack,  // ✅ Pass MediaStreamTrack directly
  videoSource: false
});
```

### 2. Audio Constraints Available

When `audioSource: true`, daily-js uses browser defaults. To customize:

```typescript
// After joining, update input settings
await call.updateInputSettings({
  audio: {
    settings: {
      echoCancellation: true,      // ✅ Remove echo
      noiseSuppression: true,      // ✅ Remove background noise
      autoGainControl: true,       // ✅ Auto volume adjustment
      deviceId: audioDeviceId,     // ✅ Specific device
      latency: 0.01               // ✅ Low latency
    }
  }
});
```

### 3. How daily-js Gets Microphone Access

```
User Action (Start Call)
    ▼
Browser Permission Request
    ▼
OS Permission (macOS/Windows/Android/iOS)
    ▼
Microphone Hardware Access
    ▼
MediaStreamTrack Created
    ▼
daily-js Receives Audio Stream
    ▼
WebRTC Encoding (Opus codec)
    ▼
Network Transmission
```

### 4. Audio Input Lifecycle

```typescript
// Phase 1: Call Object Created (audio paused)
const call = await DailyIframe.createCallObject({
  audioSource: true
});

// Phase 2: Join Room (audio starts capturing)
await call.join({ url: roomUrl, token });
// ✅ Microphone now actively capturing

// Phase 3: Configure Audio (optional optimization)
await call.updateInputSettings({
  audio: {
    settings: {
      noiseSuppression: true
    }
  }
});

// Phase 4: Toggle Audio On/Off
call.setLocalAudio(false);  // Mute
call.setLocalAudio(true);   // Unmute

// Phase 5: Leave/Destroy (audio stops)
await call.leave();
call.destroy();
```

---

## 🔊 Audio Output Management

### 1. How daily-js Handles Speaker Output

**Important:** daily-js doesn't directly control speaker output at initialization time.

```typescript
// ❌ This is INVALID (doesn't exist in daily-js)
const call = await DailyIframe.createCallObject({
  audioOutput: true  // ❌ Not a valid property!
});

// ✅ Correct: Audio output is automatic when joining
await call.join({ url: roomUrl });
// Browser automatically routes audio to default speaker
```

### 2. Audio Output Device Selection

```typescript
// List available audio output devices
const devices = await call.enumerateDevices();
const speakers = devices.filter(d => d.kind === 'audiooutput');
// Example: [
//   { deviceId: 'default', groupId: '...', kind: 'audiooutput', label: 'Speaker' },
//   { deviceId: 'bluetooth-id', groupId: '...', kind: 'audiooutput', label: 'Bluetooth Headset' }
// ]

// Switch to specific speaker device
await call.setOutputDeviceAsync({
  outputDeviceId: 'bluetooth-id'
});
// ✅ All call audio now plays through Bluetooth
```

### 3. Audio Output Control Per Platform

| Platform | Method | Details |
|----------|--------|---------|
| **Web** | setOutputDeviceAsync() | Uses Browser Audio Output Devices API |
| **Expo Web** | setOutputDeviceAsync() | Browser audio output selection |
| **iOS (RN)** | setNativeInCallAudioMode() | Native layer handles speaker routing |
| **Android (RN)** | setNativeInCallAudioMode() | Native layer handles speaker routing |

---

## 🎚️ Audio Quality Configuration

### 1. Noise Suppression

```typescript
// Enable noise suppression (removes background noise)
await call.updateInputSettings({
  audio: {
    settings: {
      noiseSuppression: true  // ✅ Default: true for voice apps
    }
  }
});

// Check current setting
const constraints = await call.getInputSettings();
console.log(constraints.audio.settings.noiseSuppression); // true
```

**How it works:**
- Browser/OS analyzes audio frequency patterns
- Identifies non-speech sounds (keyboard typing, fan noise, etc.)
- Removes or suppresses those frequencies
- Keeps human speech intact

### 2. Echo Cancellation

```typescript
// Enable echo cancellation (removes your own voice echo)
await call.updateInputSettings({
  audio: {
    settings: {
      echoCancellation: true  // ✅ Default: true
    }
  }
});
```

**When needed:**
- User has external speakers instead of headset
- Speaker audio loops back into microphone
- Listener hears their own voice delayed

### 3. Auto Gain Control

```typescript
// Enable automatic volume normalization
await call.updateInputSettings({
  audio: {
    settings: {
      autoGainControl: true  // ✅ Default: true
    }
  }
});
```

**What it does:**
- Automatically adjusts microphone gain (volume level)
- Keeps audio at consistent level regardless of proximity to mic
- Prevents very loud or very quiet audio

### 4. Optimal Settings for Voice-First Apps

```typescript
async function optimizeAudioForVoice(call) {
  try {
    await call.updateInputSettings({
      audio: {
        settings: {
          // Speech enhancement
          noiseSuppression: true,
          echoCancellation: true,
          autoGainControl: true,

          // Quality parameters
          sampleSize: 16,        // 16-bit audio
          sampleRate: 16000,     // 16 kHz (ideal for speech)

          // Prevent feedback
          latency: 0.01,         // 10ms latency

          // Device (if known)
          deviceId: 'default'
        }
      }
    });

    console.log('✅ Audio optimized for voice');
  } catch (error) {
    console.error('Audio optimization failed:', error);
  }
}
```

---

## 📱 Device Enumeration & Selection

### 1. List All Audio Devices

```typescript
async function getAudioDevices(call) {
  const devices = await call.enumerateDevices();

  const audioInputs = devices.filter(d => d.kind === 'audioinput');
  const audioOutputs = devices.filter(d => d.kind === 'audiooutput');

  console.log('Available Microphones:');
  audioInputs.forEach(d => {
    console.log(`  - ${d.label} (${d.deviceId})`);
  });

  console.log('Available Speakers:');
  audioOutputs.forEach(d => {
    console.log(`  - ${d.label} (${d.deviceId})`);
  });

  return { audioInputs, audioOutputs };
}
```

### 2. Switch Microphone Device

```typescript
async function switchMicrophone(call, deviceId) {
  try {
    await call.setInputDevicesAsync({
      audioDeviceId: deviceId  // ✅ Switch to specific mic
    });
    console.log(`✅ Switched to microphone: ${deviceId}`);
  } catch (error) {
    console.error('Failed to switch microphone:', error);
  }
}

// Usage
const devices = await call.enumerateDevices();
const secondMic = devices.find(d => d.kind === 'audioinput' && d.deviceId !== 'default');
if (secondMic) {
  await switchMicrophone(call, secondMic.deviceId);
}
```

### 3. Switch Speaker Device

```typescript
async function switchSpeaker(call, deviceId) {
  try {
    const result = await call.setOutputDeviceAsync({
      outputDeviceId: deviceId  // ✅ Switch to specific speaker
    });
    console.log(`✅ Switched to speaker: ${deviceId}`);
    return result;
  } catch (error) {
    console.error('Failed to switch speaker:', error);
  }
}

// Usage - Switch to Bluetooth if available
const devices = await call.enumerateDevices();
const bluetooth = devices.find(d =>
  d.kind === 'audiooutput' &&
  d.label.toLowerCase().includes('bluetooth')
);
if (bluetooth) {
  await switchSpeaker(call, bluetooth.deviceId);
}
```

---

## ✅ Best Practices

### 1. For Voice-First Applications

```typescript
async function initializeVoiceCall() {
  // 1. Create call with audio only
  const call = await DailyIframe.createCallObject({
    videoSource: false,     // ✅ No video
    audioSource: true,      // ✅ Enable audio
    receiveSettings: {
      video: { subscribeToAll: false }
    }
  });

  // 2. Join room
  await call.join({ url: roomUrl, token });

  // 3. Optimize audio for voice
  await call.updateInputSettings({
    audio: {
      settings: {
        noiseSuppression: true,
        echoCancellation: true,
        autoGainControl: true
      }
    }
  });

  return call;
}
```

### 2. For Permission Handling

```typescript
async function requestAudioPermission() {
  try {
    // This triggers browser permission dialog
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        noiseSuppression: true,
        echoCancellation: true
      },
      video: false
    });

    // Permission granted, stop the stream
    stream.getTracks().forEach(track => track.stop());
    return true;
  } catch (error) {
    console.error('Audio permission denied:', error);
    return false;
  }
}
```

### 3. Error Handling

```typescript
async function configureAudioSafely(call) {
  try {
    // Try to optimize
    await call.updateInputSettings({
      audio: {
        settings: {
          noiseSuppression: true,
          echoCancellation: true
        }
      }
    });
  } catch (error) {
    if (error.message.includes('NotAllowedError')) {
      console.warn('⚠️ Audio permission denied');
    } else if (error.message.includes('NotFoundError')) {
      console.warn('⚠️ No audio device found');
    } else {
      console.error('Audio configuration error:', error);
    }
  }
}
```

---

## 🔧 Implementation Guide for Story 3.8

### Current Implementation Analysis

**File:** `mobile/src/services/daily.service.ts`

#### What We Got Right ✅
```typescript
const call = await DailyIframe.createCallObject({
  videoSource: false,        // ✅ Correct: No video
  audioSource: true,         // ✅ Correct: Enable audio
  receiveSettings: { ... }   // ✅ Correct: Configuration
});
```

#### What We Fixed ✅
```typescript
// ❌ REMOVED: audioOutput: true (invalid property)
// ✅ ADDED: Comment explaining audio output is system-managed
```

#### What We Should Add for Audio Quality 🔧

**Option 1: Basic Audio Optimization (Recommended)**

```typescript
export async function configureAudio(
  call: DailyCallObject,
  config: AudioConfig = {}
): Promise<void> {
  try {
    const {
      audioInputEnabled = true,
      noiseSuppression = true,
      echoCancellation = true,
    } = config;

    // Enable/disable microphone
    if (audioInputEnabled !== undefined) {
      call.setLocalAudio(audioInputEnabled);
    }

    // ✅ NEW: Optimize audio quality after joining
    // This should be called AFTER joining the room
    await call.updateInputSettings({
      audio: {
        settings: {
          noiseSuppression,      // Remove background noise
          echoCancellation,      // Remove echo
          autoGainControl: true  // Auto volume
        }
      }
    });

    if (__DEV__) {
      console.log('[Daily] Audio optimized:', {
        audioInputEnabled,
        noiseSuppression,
        echoCancellation
      });
    }
  } catch (error) {
    if (__DEV__) {
      console.error('[Daily] Audio configuration failed:', error);
    }
    throw new Error(`Audio configuration failed`);
  }
}
```

**Option 2: Advanced Audio Management**

```typescript
export async function getAvailableAudioDevices(
  call: DailyCallObject
): Promise<{
  microphones: MediaDeviceInfo[];
  speakers: MediaDeviceInfo[];
}> {
  const devices = await call.enumerateDevices();
  return {
    microphones: devices.filter(d => d.kind === 'audioinput'),
    speakers: devices.filter(d => d.kind === 'audiooutput')
  };
}

export async function switchAudioDevice(
  call: DailyCallObject,
  deviceId: string,
  type: 'input' | 'output'
): Promise<void> {
  try {
    if (type === 'input') {
      await call.setInputDevicesAsync({ audioDeviceId: deviceId });
    } else {
      await call.setOutputDeviceAsync({ outputDeviceId: deviceId });
    }
  } catch (error) {
    throw new Error(`Failed to switch audio device: ${error}`);
  }
}
```

---

## 🎯 Key Takeaways

### What daily-js Does
✅ Manages WebRTC audio streams
✅ Handles microphone input
✅ Provides device enumeration
✅ Applies audio constraints (noise suppression, echo cancellation)
✅ Controls audio transmission (mute/unmute)

### What daily-js Does NOT Do
❌ Directly control speaker hardware (OS/browser handles this)
❌ Has an "audioOutput" property in createCallObject()
❌ Manage speaker device selection directly (but provides API)
❌ Handle platform-specific audio routing (native layer does this)

### Platform Differences

| Aspect | Web | React Native |
|--------|-----|--------------|
| **Audio Source** | mediaDevices API | Native audio capture |
| **Device Selection** | Browser Audio Output API | setNativeInCallAudioMode() |
| **Constraints** | MediaTrackConstraints | Native audio config |
| **Speaker Control** | setOutputDeviceAsync() | Native routing |

---

## 📊 Audio Flow Diagram

```
User Voice
    ↓
OS Microphone Hardware
    ↓
Browser/Native Audio Engine
    ↓
MediaStreamTrack (raw audio)
    ↓
daily-js (audioSource: true)
    ↓
Audio Constraints Applied
├─ Noise Suppression ✅
├─ Echo Cancellation ✅
└─ Auto Gain Control ✅
    ↓
Opus Audio Codec (compression)
    ↓
WebRTC Encoding
    ↓
Network Transmission
    ↓
Remote Participant Receives Audio
    ↓
Decoding → Speaker Playback
```

---

## 🚀 Conclusion

**daily-js** provides a comprehensive, well-designed audio integration API:

1. **Initialization:** Configure audio source via `createCallObject()`
2. **Optimization:** Fine-tune quality via `updateInputSettings()`
3. **Control:** Toggle audio on/off via `setLocalAudio()`
4. **Device Management:** Switch devices via `setInputDevicesAsync()` and `setOutputDeviceAsync()`
5. **Enumeration:** List devices via `enumerateDevices()`

**For Story 3.8 (voice-first app):**
- ✅ Current implementation is correct
- ✅ Audio input/output are properly configured
- ⚠️ Consider adding audio quality optimization via `updateInputSettings()`
- 🎯 Audio quality already handled by WebRTC defaults

**Status:** Story 3.8 ready for production with current audio configuration.
