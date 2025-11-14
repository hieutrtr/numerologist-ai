# Voice Bot Mobile App
## React Native Frontend with Daily.co Integration

A production-ready React Native mobile app for voice AI conversations using Daily.co WebRTC.

## Features

✅ **Voice Conversation Management**
- Start/end conversations with one tap
- Real-time connection status
- Bot presence detection
- Mute/unmute control

✅ **Daily.co WebRTC Integration**
- Audio-only calls (no video)
- Automatic room joining
- Event handling (participants, tracks)
- Cleanup and error handling

✅ **Beautiful UI**
- Voice activity visualization
- Connection status indicators
- Loading states
- Error handling

✅ **Cross-Platform**
- iOS support
- Android support
- Expo managed workflow

## Quick Start

### Prerequisites

- Node.js 18+
- npm or yarn
- Expo CLI: `npm install -g expo-cli`
- iOS: Xcode (Mac only)
- Android: Android Studio

### Installation

```bash
cd mobile
npm install
```

### Configuration

Edit `src/services/api.ts` and update the API URL:

```typescript
const API_BASE_URL = __DEV__
  ? 'http://YOUR_LOCAL_IP:8000/api/v1'  // Use your computer's IP
  : 'https://your-api.com/api/v1';
```

**Important for iOS Simulator**: Use your computer's local IP address (e.g., `192.168.1.10`) instead of `localhost`.

### Running the App

```bash
# Start Metro bundler
npm start

# Run on iOS
npm run ios

# Run on Android
npm run android
```

## Project Structure

```
mobile/
├── App.tsx                           # Entry point
├── app.json                          # Expo configuration
├── package.json                      # Dependencies
├── tsconfig.json                     # TypeScript config
├── babel.config.js                   # Babel transforms (NativeWind)
├── metro.config.js                   # Metro bundler (CSS processing)
├── tailwind.config.js                # Tailwind design system
├── postcss.config.js                 # PostCSS plugins
├── global.css                        # Tailwind entry point
├── nativewind-env.d.ts              # TypeScript types for className
└── src/
    ├── components/
    │   ├── VoiceVisualizer.tsx       # Voice activity animation
    │   └── ConnectionStatus.tsx      # Status indicator
    ├── hooks/
    │   └── useConversation.ts        # Conversation management hook
    ├── screens/
    │   └── ConversationScreen.tsx    # Main screen
    ├── services/
    │   └── api.ts                    # Backend API client
    ├── types/                        # TypeScript types
    ├── store/                        # State management (optional)
    └── utils/                        # Utilities
```

## Styling System

This boilerplate uses **NativeWind v4** - Tailwind CSS for React Native.

### Why NativeWind?

- ✅ **Familiar**: Use Tailwind utility classes
- ✅ **Fast**: Write styles faster than StyleSheet
- ✅ **Type-safe**: Full TypeScript autocomplete
- ✅ **Design system**: Centralized in `tailwind.config.js`
- ✅ **Tree-shaking**: Only used classes bundled

### Usage Example

```tsx
import { View, Text } from 'react-native';

export default function MyComponent() {
  return (
    <View className="bg-primary p-4 rounded-lg">
      <Text className="text-white text-lg font-bold">
        Hello World
      </Text>
    </View>
  );
}
```

### Available Utilities

**Colors**: `bg-primary`, `text-secondary`, `border-error`
**Spacing**: `p-4`, `m-2`, `px-lg`, `mt-md`
**Typography**: `text-lg`, `font-bold`, `text-center`
**Layout**: `flex-1`, `flex-row`, `items-center`, `justify-between`
**Size**: `w-full`, `h-32`, `min-h-screen`

### Customization

All design tokens in `tailwind.config.js`:
- Colors (primary, secondary, etc.)
- Spacing (xs, sm, md, lg, xl)
- Typography (text sizes and weights)

**Learn More**: See `docs/FRONTEND_CONFIG_EXPLAINED.md` for:
- How Babel, Metro, Tailwind work together
- Build pipeline explanation
- Adding custom colors/spacing/fonts
- Debugging styling issues

## Core Components

### useConversation Hook

Manages the complete conversation lifecycle:

```typescript
const {
  state,              // Connection state
  startConversation,  // Start new conversation
  endConversation,    // End and cleanup
  toggleMute,         // Mute/unmute mic
  isMuted             // Current mute state
} = useConversation();
```

### API Client

Handles backend communication:

```typescript
// Start conversation
const response = await apiClient.startConversation();
// Returns: { conversation_id, daily_room_url, daily_token }

// End conversation
await apiClient.endConversation(conversationId);
```

### Daily.co Integration

WebRTC audio connection:

```typescript
const callObject = Daily.createCallObject({
  audioSource: true,   // Enable microphone
  videoSource: false,  // Audio only
});

await callObject.join({
  url: roomUrl,
  token: token
});
```

## Permissions

### iOS (Info.plist)

Already configured in `app.json`:

```xml
<key>NSMicrophoneUsageDescription</key>
<string>This app needs microphone access for voice conversations</string>
```

### Android (AndroidManifest.xml)

Already configured in `app.json`:

```xml
<uses-permission android:name="android.permission.RECORD_AUDIO" />
<uses-permission android:name="android.permission.MODIFY_AUDIO_SETTINGS" />
```

## Customization

### Change API Endpoint

Edit `src/services/api.ts`:

```typescript
const API_BASE_URL = 'https://your-production-api.com/api/v1';
```

### Add Authentication

Update `api.ts` to include auth token:

```typescript
// Set token after login
apiClient.setAuthToken(userToken);

// Token will be included in all requests
```

### Customize UI Colors

**Option 1: Tailwind (Recommended)**

Edit `tailwind.config.js`:
```javascript
colors: {
  primary: {
    DEFAULT: '#FF6B6B',  // Your brand color
    dark: '#CC5555',
    light: '#FFE5E5',
  }
}
```

Then use in components:
```tsx
<View className="bg-primary" />
<Text className="text-primary-dark" />
```

**Option 2: StyleSheet**

Edit component styles directly:
- `src/screens/ConversationScreen.tsx`
- `src/components/VoiceVisualizer.tsx`

**Learn More**: See `docs/FRONTEND_CONFIG_EXPLAINED.md` for complete styling guide

### Add More Screens

1. Create screen in `src/screens/`
2. Add route in `App.tsx`:

```typescript
<Stack.Screen name="YourScreen" component={YourScreen} />
```

## Testing

### Test on Physical Device

```bash
# iOS
expo start --ios

# Android
expo start --android

# Scan QR code with Expo Go app
```

### Test with Local Backend

1. Start backend: `uvicorn main:app --host 0.0.0.0`
2. Find your computer's IP: `ifconfig` (Mac/Linux) or `ipconfig` (Windows)
3. Update `api.ts` with your IP: `http://192.168.1.X:8000/api/v1`
4. Start mobile app: `npm start`

## Troubleshooting

### "Unable to connect to API"

- Check backend is running
- Use computer's IP instead of `localhost`
- Ensure devices are on same network
- Check firewall settings

### "Microphone permission denied"

- Go to device Settings → App → Permissions
- Enable Microphone permission
- Restart the app

### "Daily.co connection failed"

- Check Daily.co API key in backend
- Verify room creation succeeded
- Check network connectivity
- Try on different network (some corporate networks block WebRTC)

### Audio not working on iOS

- Check Silent mode is off
- Verify audio permissions granted
- Try restarting the app

### Metro bundler issues

```bash
# Clear cache
npm start -- --reset-cache

# Clear node_modules
rm -rf node_modules
npm install
```

## Building for Production

### iOS

```bash
# Build with EAS (Expo Application Services)
eas build --platform ios

# Or build locally
expo build:ios
```

Requirements:
- Apple Developer account ($99/year)
- Xcode installed

### Android

```bash
# Build APK
eas build --platform android

# Or build locally
expo build:android
```

Requirements:
- Google Play Developer account ($25 one-time)

## Performance Optimization

### Reduce Bundle Size

- Remove unused dependencies
- Enable Hermes engine (Android)
- Optimize images

### Improve Startup Time

- Lazy load screens
- Optimize splash screen
- Use native modules sparingly

## Future Enhancements

- [ ] Add conversation history
- [ ] Implement message transcription display
- [ ] Add voice amplitude visualization
- [ ] Support landscape mode
- [ ] Add settings screen
- [ ] Implement push notifications
- [ ] Add offline mode support

## Dependencies

### Core

- **React Native** - Mobile framework
- **Expo** - Development tooling
- **TypeScript** - Type safety

### Voice/Audio

- **@daily-co/react-native-daily-js** - WebRTC client
- **expo-av** - Audio permissions and playback

### Networking

- **axios** - HTTP client

### Navigation

- **@react-navigation/native** - Screen navigation
- **@react-navigation/stack** - Stack navigator

### UI/Animation

- **react-native-reanimated** - Smooth animations
- **react-native-gesture-handler** - Touch handling

## License

MIT License - See LICENSE file

## Support

- **Issues**: Create issue in repository
- **Documentation**: See parent boilerplate README
- **Backend Setup**: See `../backend/README.md`

---

**Ready to run?** Follow the Quick Start section above and you'll have the app running in 5 minutes!