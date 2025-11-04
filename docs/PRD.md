# Numerologist AI - Product Requirements Document

**Author:** Hieu
**Date:** 2025-11-03
**Version:** 1.0

---

## Executive Summary

Numerologist AI transforms how people access numerology guidance by replacing static readings with natural voice conversations. Users speak with an AI assistant that acts as a master Pythagorean numerologist, providing personalized insights, answering questions, and offering guidance through voice interaction - anytime, anywhere.

The product addresses the fundamental friction in traditional numerology: it's text-heavy, generic, and non-interactive. By making numerology conversational and voice-first, we make ancient wisdom accessible to modern users who want guidance on-the-go.

### What Makes This Special

**The magic of Numerologist AI is the natural conversation itself** - users don't read about their life path number, they *talk about it*. The AI responds to their specific questions, explores their concerns, and guides them through interpretations in real-time. It's like having a personal numerologist available 24/7, but powered by cutting-edge voice AI technology.

What makes users say "wow": The moment they realize the AI truly understands their question about their life and responds with personalized numerology insights through natural conversation.

---

## Project Classification

**Technical Type:** Mobile App (React Native - Web + Android)
**Domain:** Consumer Wellness/Spirituality
**Complexity:** Medium (Voice AI integration, real-time communication, knowledge synthesis)

**Classification Rationale:**
- Mobile-first voice application with cross-platform deployment
- Consumer-focused product requiring excellent UX and voice experience
- Integration of multiple AI services (STT, LLM, TTS) orchestrated through Pipecat-ai
- Not a regulated domain, but requires content quality and cultural sensitivity
- Real-time voice streaming with low-latency requirements

---

## Success Criteria

**MVP Success means:**

1. **The Conversation Works Beautifully**
   - Users complete 8-12 minute voice sessions without friction
   - Voice recognition accuracy >85% for clear speech
   - Response latency <3 seconds maintaining natural conversation flow
   - Users can interrupt and the AI responds naturally

2. **Users Experience the Magic**
   - Users complete their first conversation and immediately understand their life path number
   - The "aha moment": Users realize they can ask follow-up questions and get personalized answers
   - User satisfaction: 4.5+ star ratings with comments mentioning "felt like talking to a real numerologist"

3. **Technical Foundation is Solid**
   - App deploys successfully on web (PWA) and Android
   - Voice pipeline (Deepgram → GPT → ElevenLabs) orchestrates reliably through Pipecat-ai
   - No critical bugs that block core conversation functionality
   - 50+ beta users complete successful sessions

4. **Engagement Shows Value**
   - 40% of users return within 30 days (strong retention signal)
   - 20% of registered users are daily active (deep engagement)
   - Users average 3-5 sessions per week
   - Average 10+ voice exchanges per session (showing depth of conversation)

**Success is NOT just numbers - it's when users tell friends: "I had the most amazing conversation with this AI numerologist"**

### Business Metrics

**Launch Goals (First 3 Months):**
- 1,000 active users (validation of product-market fit)
- 40% 30-day retention, 20% 90-day retention
- Cost per conversation <$0.15 (sustainability target)
- 15% viral coefficient (users inviting friends)

**Growth Phase (Months 4-12):**
- 10,000 active users
- 5% conversion to premium tier (freemium monetization)
- $50,000 MRR from subscriptions
- Maintain 4.5+ star rating across app stores

**North Star Metric:**
**Total meaningful conversations per week** - measures both user count and engagement depth. A "meaningful conversation" = 5+ minutes with 8+ voice exchanges.

---

## Product Scope

### MVP - Minimum Viable Product

**Core Voice Experience:**
- Natural voice-to-voice conversation with AI numerologist (no typing required)
- Real-time speech recognition via Deepgram
- AI reasoning via Azure OpenAI GPT-5-mini
- Natural voice synthesis via ElevenLabs
- Pipecat-ai orchestrating the voice pipeline through Daily.co
- Interrupt handling for natural conversational flow

**Numerology Knowledge & Calculations:**
- Life Path Number calculation and detailed interpretation
- Expression/Destiny Number analysis
- Soul Urge/Heart's Desire Number insights
- Birthday Number meanings
- Personal Year calculations
- Comprehensive Pythagorean numerology knowledge base

**User Management:**
- User registration with name and birth date
- Secure authentication
- Basic profile management
- Conversation history storage (what was discussed, key insights)
- Context retention across sessions (AI remembers previous conversations)

**Mobile Application (React Native):**
- Web PWA deployment (works in mobile browsers)
- Android native app
- Clean, minimal UI with voice-first design philosophy
- Visual display of calculated numbers during conversation
- Recording indicator when voice is active
- Basic settings: voice speed, volume, notification preferences

**Essential UX:**
- Onboarding flow: microphone permission, voice introduction, first calculation
- Visual feedback during conversation (voice animation, transcription display)
- Ability to pause/resume conversations
- Clear error handling for connection/voice issues

**Scoped OUT of MVP:**
- iOS native app (Phase 2)
- Payment processing/subscriptions
- Social sharing features
- Multiple voice personality options
- Compatibility/relationship readings (two-person numerology)
- Conversation search/replay
- Offline mode
- Multiple languages
- Advanced personalization algorithms

### Growth Features (Post-MVP)

**Phase 2 - Enhanced Experience (Months 4-6):**
- iOS native app launch
- Relationship compatibility readings (compare two people's numerology)
- Daily numerology insights via push notifications
- Conversation history with search and replay capability
- Social sharing: screenshot insights, invite friends
- Multiple AI voice options (male/female, different accents)
- Enhanced conversation memory (long-term context)

**Phase 3 - Monetization & Community (Months 7-9):**
- Freemium model: 5 free conversations/month
- Premium subscription ($9.99/month): unlimited conversations
- In-depth numerology reports (PDF/email delivery)
- Extended guidance sessions (30+ minute conversations)
- User community features (forums, shared insights)
- Content library: guided meditations, numerology education

### Vision (Future)

**Year 2+ - Platform Evolution:**
- Multi-practice integration: astrology, tarot, I Ching
- AI learns individual communication style for deeper personalization
- Voice journal integration for tracking personal growth
- Group sessions: couple's readings, family numerology
- Expert consultations: connect with human numerologists
- API for third-party integrations
- White-label solution for wellness practitioners
- Predictive insights using AI + numerology patterns

**The Ultimate Vision:**
A comprehensive personal guidance platform where ancient wisdom meets modern AI, accessible through natural conversation, helping millions find clarity and direction in their lives.

---

## Innovation & Novel Patterns

### Voice-First Spirituality Platform

**What's Novel:**
Numerologist AI pioneers **voice-first access to spiritual guidance**. While astrology and numerology apps exist, they're all text-based calculators. We're the first to enable natural conversation with an AI expert in this domain.

**Key Innovations:**

1. **Conversational Numerology Knowledge**
   - Traditional: Static readings from pre-written text
   - Our approach: AI synthesizes numerology principles in response to user's specific life questions
   - Innovation: Dynamic interpretation based on conversation context

2. **Voice-Only Interaction for Spiritual Practice**
   - Removes the friction of typing/reading for personal guidance
   - Enables use during meditation, morning routines, commutes
   - Makes spiritual guidance accessible while multitasking

3. **Context-Aware Guidance Across Sessions**
   - AI remembers previous conversations and life context
   - Can reference past readings when answering new questions
   - Builds a longitudinal understanding of the user's journey

4. **Real-Time Voice Pipeline for Mystical Content**
   - Technical challenge: Low-latency voice AI for sensitive, nuanced spiritual content
   - Must balance speed with thoughtful, meaningful responses
   - Orchestrating multiple AI services (Pipecat-ai) for seamless experience

### Validation Approach

**Hypothesis to Test:**
Users seeking spiritual guidance prefer voice conversation over reading text.

**Validation Methods:**

1. **Early Beta Testing (Month 3)**
   - 50 beta users from target demographic
   - A/B test: Voice-only vs Voice+Text hybrid
   - Measure: engagement time, return rate, qualitative feedback

2. **Quality Metrics:**
   - User ratings specifically on "felt like talking to real numerologist"
   - Track conversation depth (number of follow-up questions)
   - Monitor drop-off points in conversation flow

3. **Voice UX Validation:**
   - Test with various accents, speech patterns, background noise
   - Measure voice recognition accuracy across demographics
   - Validate interrupt handling feels natural

4. **Content Accuracy:**
   - Expert numerologist review of AI responses
   - User survey: "Did the reading resonate with you?"
   - Track questions that AI struggles to answer (knowledge gaps)

**Success Signals:**
- Users complete 8+ minute conversations (shows engagement)
- 40%+ return within 7 days (validates value)
- NPS score >40 (users recommend to friends)
- Low reliance on fallback to text interface

**Risk Mitigation:**
- Fallback option: If voice fails, offer text chat
- Content safety: AI prompt engineering to avoid harmful advice
- Cost management: Session limits during beta to control API costs

---

## Mobile App Specific Requirements

### Platform Support

**MVP Platforms:**
- **Web (PWA)**: Progressive Web App optimized for mobile browsers
  - Chrome, Safari, Firefox on Android/iOS
  - Installation prompt for "add to home screen"
  - Responsive design: 320px - 428px width (mobile devices)
  - Works offline for UI (voice requires connection)

- **Android Native**: React Native build for Google Play Store
  - Minimum SDK: Android 8.0 (API level 26)
  - Target SDK: Android 14 (API level 34)
  - Support for Android phones and tablets
  - Google Play Store compliance (content ratings, permissions)

**Post-MVP:**
- **iOS Native**: React Native build for App Store (Phase 2)
  - iOS 14+ support
  - iPhone and iPad optimization
  - App Store guidelines compliance

### Device Capabilities

**Required Permissions:**
- **Microphone Access** (Critical): For voice input via Deepgram
  - Must explain clearly why needed (voice conversation)
  - Graceful degradation if denied (explain can't work without voice)
  - Runtime permission request on Android

- **Internet Access** (Critical): Real-time voice streaming via Daily.co
  - Minimum bandwidth: 128 kbps for voice quality
  - Handle poor connections gracefully
  - Show connection quality indicator

- **Storage** (Standard): Local caching and conversation history
  - Store user profile data locally
  - Cache recent conversation summaries
  - Keep numerology calculation results

**Optional Permissions:**
- **Notifications** (Post-MVP): For daily insights, reminders
  - Request after user completes first conversation
  - Never required for core functionality

**Device Features Utilized:**
- Audio input/output (speakers, microphone, headphones)
- Network status detection (WiFi vs cellular)
- Wake lock during active conversation (prevent screen sleep)
- Background audio handling (continues if app backgrounded)

### Mobile-Specific Considerations

**Performance Optimization:**
- App bundle size <50 MB for fast downloads
- Launch time <3 seconds on mid-range devices
- Voice latency optimization for mobile networks
- Efficient battery usage (voice processing, network)

**Network Handling:**
- Graceful degradation on poor networks
  - Show "reconnecting" during interruptions
  - Buffer audio for smoother playback
  - Queue failed messages for retry
- Offline mode (limited):
  - Show cached conversation history
  - Display calculated numbers from previous sessions
  - Clear messaging: "Voice requires connection"

**App Store Compliance:**
- **Google Play Store**:
  - Content rating: Teen (spiritual content)
  - Privacy policy required
  - Data safety section (microphone, personal data)
  - In-app purchases disclosure (post-MVP)

- **Apple App Store** (Phase 2):
  - Similar content rating and privacy requirements
  - App Tracking Transparency compliance
  - Sign in with Apple option

### Mobile UX Patterns

**Native Gestures:**
- Swipe to dismiss conversation
- Pull-to-refresh conversation history
- Tap to activate/deactivate microphone
- Long-press to see conversation options

**Mobile-First Design:**
- Large touch targets (minimum 44x44 dp)
- Bottom-sheet UI for settings (thumb-reachable)
- Floating action button for quick access to new conversation
- Haptic feedback for key interactions (mic on/off)

**Orientation:**
- Portrait primary (locked during conversation)
- Landscape optional for tablets
- Handle rotation gracefully

### Authentication & Authorization

**MVP Authentication:**
- Email + password registration
- OAuth integration:
  - Google Sign-In (priority for Android)
  - Apple Sign-In (iOS requirement for Phase 2)
- Password reset via email
- Session management (7-day tokens)

**Security:**
- Encrypted storage of auth tokens
- HTTPS only for all API calls
- Secure WebRTC connections for voice streams
- No storage of raw voice data (privacy-first)

**User Roles** (Simple for MVP):
- Free User: Access to core conversations
- Premium User: Unlimited conversations (post-MVP)
- Admin: Content management, user support

---

## User Experience Principles

### Design Philosophy: Voice-First, Visually Minimal

The UI exists to *support* the conversation, not compete with it. The voice is the star.

### Core UX Principles

**1. Calm and Present**
- Soft, spiritual aesthetic (deep purples, golds, calming gradients)
- Minimal visual noise during conversation
- Soothing animations that respond to voice
- Think: meditation app meets voice assistant

**2. Trust and Intimacy**
- Warm, welcoming voice and visuals
- Personal touch: uses user's name naturally
- Feeling of privacy and confidentiality
- No aggressive marketing or interruptions

**3. Accessible and Inclusive**
- Works for various accents and speech patterns
- Clear visual feedback for hearing-impaired (transcriptions)
- Simple enough for non-tech-savvy spiritual seekers
- Culturally sensitive imagery and language

**4. Delightful and Magical**
- Surprise moments: gentle animations when numbers are revealed
- Easter eggs: special responses for milestones (100th conversation)
- Shareable moments: beautiful visual cards of key insights
- Voice personality: wise, warm, slightly mystical but not cheesy

### Visual Design Language

**Color Palette:**
- Primary: Deep purple (#6B46C1) - spirituality, wisdom
- Secondary: Gold (#F6B93B) - divine, special moments
- Background: Dark gradient (#1A1A2E to #16213E) - cosmic, calm
- Text: Soft white (#F5F5F5) with subtle glow

**Typography:**
- Headings: Elegant serif (Playfair Display) for numerology numbers
- Body: Clean sans-serif (Inter) for readability
- Large, readable text (min 16px) for mobile

**Motion:**
- Voice amplitude visualization (organic wave forms)
- Number reveals: fade in with slight scale animation
- Transitions: smooth 300-400ms ease curves
- Loading states: gentle pulsing, never harsh spinners

### Key Interactions

**Onboarding Flow:**
1. Welcome screen: "Meet your AI numerologist"
2. Microphone permission with clear explanation
3. Voice test: "Tell me your name" (validates mic works)
4. Quick tutorial: Show mic button, explain how to interrupt
5. First calculation: "What's your birth date?"
6. Magic moment: AI speaks their Life Path Number

**Primary Conversation Screen:**
```
┌─────────────────────────┐
│     [Status Bar]        │
├─────────────────────────┤
│                         │
│   [Amplitude Wave]      │ ← Voice visualization
│                         │
│   "Your Life Path       │
│    Number is 7"         │ ← Number display (large)
│                         │
│   [Live Transcription]  │ ← What user just said
│                         │
│   ┌─────────────────┐   │
│   │  [Mic Button]   │   │ ← Central, prominent
│   └─────────────────┘   │
│                         │
│   [Settings] [History]  │ ← Bottom nav
└─────────────────────────┘
```

**Microphone Interaction:**
- Tap to talk (push-to-talk mode optional)
- Visual feedback: pulsing glow when listening
- Color change: blue (listening) → purple (AI speaking)
- Haptic feedback on tap (mobile)

**Interrupt Handling:**
- User can tap mic or speak to interrupt AI mid-response
- Visual: "Listening..." appears immediately
- AI pauses gracefully: "Oh, go ahead..."

**Conversation History:**
- Swipe right from edge to see past conversations
- Each conversation shows: date, main topic, key insight
- Tap to see transcript and numbers discussed
- Long-press to delete

**Settings Screen:**
- Voice speed slider (0.8x - 1.2x)
- Voice volume
- Transcription on/off toggle
- Account management
- Privacy settings: delete data, opt-out of improvements

**Error States:**
- Microphone denied: Friendly explanation + settings link
- No internet: "I need connection to speak with you. Check your network?"
- Voice recognition failed: "I didn't catch that. Could you try again?"
- API error: "Give me a moment..." (brief retry, then fallback message)

### Emotional Journey

**First-Time User (Session 1):**
- Emotion: Curious, slightly uncertain
- UX Response: Warm welcome, clear guidance, quick win (calculate their number)
- Goal: Build trust, show the magic works

**Returning User (Sessions 2-5):**
- Emotion: Engaged, exploring
- UX Response: Remember context, dive deeper, offer new angles
- Goal: Demonstrate depth, encourage questions

**Power User (Sessions 10+):**
- Emotion: Connected, reliant
- UX Response: Shortcuts, advanced features, anticipate needs
- Goal: Become indispensable part of their routine

---

## Functional Requirements

### FR-1: Voice Conversation System

**FR-1.1: Real-Time Voice Input**
- System shall capture user voice input via device microphone
- Shall support continuous listening mode and push-to-talk mode
- Shall provide visual feedback during voice capture (amplitude visualization)
- Shall handle interruptions gracefully (user can interrupt AI mid-response)
- **Acceptance**: User can speak naturally and see visual confirmation

**FR-1.2: Speech-to-Text Processing**
- System shall transcribe user speech to text via Deepgram API
- Shall support various accents and speech patterns with >85% accuracy
- Shall display live transcription to user for confirmation
- Shall handle background noise with noise suppression
- **Acceptance**: User speech accurately converted to text within 1 second

**FR-1.3: AI Reasoning & Response Generation**
- System shall process user questions via Azure OpenAI GPT-5-mini
- Shall maintain conversation context across multiple exchanges
- Shall reference numerology knowledge base for accurate interpretations
- Shall generate personalized responses based on user's birth data
- **Acceptance**: AI provides relevant, accurate numerology guidance

**FR-1.4: Text-to-Speech Output**
- System shall convert AI responses to natural voice via ElevenLabs
- Shall deliver audio with <2 second latency from user speech end
- Shall support voice speed adjustment (0.8x - 1.2x)
- Shall pause/resume playback on user command
- **Acceptance**: Natural, conversational voice output with low latency

**FR-1.5: Voice Pipeline Orchestration**
- System shall orchestrate STT→LLM→TTS pipeline via Pipecat-ai framework
- Shall manage state across conversation turns
- Shall handle real-time audio streaming through Daily.co
- Shall recover gracefully from service failures (retry, fallback)
- **Acceptance**: Seamless conversation flow from user speech to AI response

### FR-2: Numerology Calculation Engine

**FR-2.1: Life Path Number**
- System shall calculate Life Path Number from birth date
- Shall provide detailed interpretation specific to the calculated number (1-9, 11, 22, 33)
- Shall explain meaning in context of user's life questions
- **Acceptance**: Accurate Pythagorean calculation with personalized interpretation

**FR-2.2: Expression/Destiny Number**
- System shall calculate from user's full birth name
- Shall interpret meaning for career, life purpose, natural talents
- **Acceptance**: Correct calculation following Pythagorean method

**FR-2.3: Soul Urge/Heart's Desire Number**
- System shall calculate from vowels in user's name
- Shall interpret inner motivations and desires
- **Acceptance**: Accurate vowel-based calculation with interpretation

**FR-2.4: Birthday Number**
- System shall identify significance of birth day (1-31)
- Shall explain special talents and characteristics
- **Acceptance**: Birth day interpretation provided conversationally

**FR-2.5: Personal Year Calculation**
- System shall calculate current Personal Year based on birth date + current year
- Shall provide guidance relevant to current year cycle
- **Acceptance**: Accurate yearly cycle calculation and interpretation

**FR-2.6: Numerology Knowledge Base**
- System shall access comprehensive Pythagorean numerology knowledge
- Shall answer questions about: number meanings, compatibility, life path guidance
- Shall synthesize knowledge dynamically based on conversation context
- **Acceptance**: AI demonstrates deep numerology expertise in responses

### FR-3: User Management

**FR-3.1: User Registration & Authentication**
- System shall support email + password registration
- Shall integrate Google OAuth for Android users
- Shall provide password reset via email
- Shall maintain secure sessions (7-day tokens)
- **Acceptance**: User can create account and sign in securely

**FR-3.2: User Profile**
- System shall store: full name, birth date, email
- Shall allow profile editing (name, birth date update)
- Shall support account deletion (GDPR compliance)
- **Acceptance**: User profile data persists across sessions

**FR-3.3: Conversation History**
- System shall save summary of each conversation (date, main topic, key insights)
- Shall store calculated numerology numbers per user
- Shall NOT store raw voice recordings (privacy-first)
- Shall allow users to view past conversations
- **Acceptance**: User can review previous conversation summaries

**FR-3.4: Context Retention**
- System shall remember previous conversations in AI context
- Shall reference past readings when relevant ("As we discussed last time...")
- Shall maintain long-term understanding of user's life journey
- **Acceptance**: AI demonstrates memory of past conversations

### FR-4: Mobile Application

**FR-4.1: Cross-Platform Deployment**
- System shall deploy as Progressive Web App (PWA) for mobile web
- Shall build native Android app via React Native
- Shall support responsive design (320px - 428px mobile width)
- **Acceptance**: App runs on web browsers and Android devices

**FR-4.2: Onboarding Flow**
- System shall guide new users through setup:
  1. Welcome and explanation
  2. Microphone permission request
  3. Voice test
  4. First numerology calculation
- **Acceptance**: 90% of new users complete onboarding

**FR-4.3: Conversation Interface**
- System shall display primary screen with:
  - Voice amplitude visualization
  - Large numerology number display
  - Live transcription
  - Central microphone button
  - Bottom navigation (Settings, History)
- **Acceptance**: Interface is intuitive, users find mic button immediately

**FR-4.4: Settings & Preferences**
- System shall allow adjustment of: voice speed, volume
- Shall toggle transcription display on/off
- Shall provide account management access
- **Acceptance**: User can customize voice experience

**FR-4.5: Network & Error Handling**
- System shall detect poor network conditions
- Shall display connection quality indicator
- Shall show friendly error messages (mic denied, no internet, API failure)
- Shall retry failed operations automatically
- **Acceptance**: User understands issues and knows how to resolve

### FR-5: Data & Privacy

**FR-5.1: Data Storage**
- System shall encrypt user data at rest
- Shall use HTTPS for all API communication
- Shall encrypt WebRTC voice streams
- **Acceptance**: All sensitive data encrypted

**FR-5.2: Privacy Controls**
- System shall allow users to delete conversation history
- Shall NOT store raw voice recordings without explicit opt-in
- Shall provide data export (GDPR requirement)
- **Acceptance**: Users control their data

**FR-5.3: Content Safety**
- System shall include AI guardrails against harmful advice
- Shall include disclaimer: "for entertainment and guidance purposes"
- Shall detect and handle sensitive topics appropriately
- **Acceptance**: No harmful or inappropriate AI responses in testing

### FR-6: Performance & Reliability

**FR-6.1: Latency Requirements**
- Voice-to-response latency SHALL be <3 seconds average
- App launch time SHALL be <3 seconds on mid-range devices
- Network requests SHALL timeout after 30 seconds with user notification
- **Acceptance**: Measured performance meets targets

**FR-6.2: Quality Standards**
- Voice recognition accuracy SHALL be >85% for clear speech
- AI response accuracy SHALL be validated by numerology expert
- App crash rate SHALL be <1% of sessions
- **Acceptance**: Quality metrics tracked and meet thresholds

**FR-6.3: Concurrent Users**
- System SHALL support 100+ concurrent voice conversations (MVP scale)
- SHALL scale to 1,000+ concurrent users (growth phase)
- **Acceptance**: Load testing confirms capacity

### Requirements Traceability

**Magic Moments Mapped:**
- FR-1.4, FR-1.5: Enable natural conversation (the core magic)
- FR-2.1, FR-2.6: AI demonstrates deep numerology expertise
- FR-3.4: AI remembers and references past conversations (building relationship)
- FR-4.3: Beautiful, calm interface supports the voice experience

**User Value:**
- Every FR connects to solving the core problem: making numerology accessible through voice
- No "nice-to-have" features in MVP - everything serves the magic moment

---

## Non-Functional Requirements

### Performance

**NFR-P1: Voice Latency** ⭐ CRITICAL
- End-to-end voice response time: <3 seconds (average)
  - Speech-to-text: <800ms
  - AI processing: <1500ms
  - Text-to-speech: <700ms
- 95th percentile: <5 seconds
- Rationale: Natural conversation requires near-instant responses

**NFR-P2: App Performance**
- Cold start launch time: <3 seconds
- Hot start launch time: <1 second
- UI interaction response: <100ms (60fps animations)
- Memory footprint: <200MB on device

**NFR-P3: Network Efficiency**
- Voice streaming: Optimized for 128kbps connections
- Adaptive quality based on network speed
- Offline UI: conversation history accessible without network
- Bandwidth usage: ~15-20 MB per 10-minute conversation

**NFR-P4: Battery Efficiency**
- Active conversation: <5% battery per 10 minutes
- Background mode: Minimal impact (<0.5% per hour)
- Wake lock only during active conversation

### Security

**NFR-S1: Data Encryption** ⭐ CRITICAL
- All data at rest encrypted (AES-256)
- All data in transit encrypted (TLS 1.3)
- WebRTC streams encrypted (DTLS-SRTP)
- Voice data never stored unencrypted

**NFR-S2: Authentication Security**
- Password requirements: Min 8 characters, mixed case, number
- OAuth 2.0 for social logins
- JWT tokens with 7-day expiration
- Refresh token rotation
- Account lockout after 5 failed attempts

**NFR-S3: API Security**
- Rate limiting: 100 requests per user per hour
- API key rotation every 90 days
- Service-to-service authentication for backend APIs
- Input sanitization to prevent injection attacks

**NFR-S4: Privacy Compliance**
- GDPR compliant (data export, right to deletion)
- No storage of raw voice recordings without explicit consent
- Clear privacy policy presented during onboarding
- User consent for data improvement/ML training

**NFR-S5: Content Safety**
- AI response filtering for harmful content
- Monitoring for inappropriate user inputs
- Automated flagging of concerning conversations
- Human review process for flagged content

### Scalability

**NFR-SC1: Concurrent Users**
- MVP: Support 100 concurrent voice conversations
- Month 3: Scale to 500 concurrent conversations
- Month 6: Scale to 1,000+ concurrent conversations
- Architecture must support horizontal scaling

**NFR-SC2: Database Scalability**
- Design for 10,000 users by Month 3
- Design for 100,000 users by Month 12
- Query performance: <100ms for user data retrieval
- Conversation history: Paginated loading (20 per page)

**NFR-SC3: API Service Limits**
- Deepgram: Handle rate limits gracefully (queue/retry)
- OpenAI: Manage token limits, cost controls
- ElevenLabs: Character limit monitoring, voice generation queue
- Daily.co: Room limit management, automatic cleanup

**NFR-SC4: Geographic Distribution**
- Serve users globally (primary: US, UK, Australia)
- CDN for static assets
- Regional API endpoints if latency issues detected

### Integration Requirements

**NFR-I1: Third-Party Service Dependencies** ⭐ CRITICAL

**Voice Pipeline Services:**
- Deepgram (Speech-to-Text)
  - SLA: 99.9% uptime
  - Fallback: Google Cloud Speech-to-Text
  - Monitoring: Track API errors, latency

- Azure OpenAI (GPT-5-mini)
  - SLA: 99.9% uptime
  - Fallback: Graceful error message, retry logic
  - Cost controls: Set monthly spending limits
  - Monitoring: Token usage, response quality

- ElevenLabs (Text-to-Speech)
  - SLA: 99.5% uptime
  - Fallback: Azure TTS or AWS Polly
  - Monitoring: Generation time, voice quality

- Daily.co (WebRTC/Real-time Communication)
  - SLA: 99.9% uptime
  - Fallback: None (critical infrastructure)
  - Monitoring: Room creation, connection quality

**NFR-I2: Pipecat-ai Orchestration**
- Must orchestrate all voice services reliably
- State management across conversation turns
- Error handling and recovery for each service
- Logging for debugging conversation flows

**NFR-I3: Service Resilience**
- Implement circuit breaker pattern for external APIs
- Retry logic: 3 attempts with exponential backoff
- Graceful degradation when services unavailable
- User-friendly error messages (never expose technical details)

**NFR-I4: Cost Management**
- Monitor per-conversation API costs
- Alert when costs exceed $0.20 per conversation
- Implement usage limits during beta (prevent runaway costs)
- Track cost trends for pricing model validation

### Accessibility

**NFR-A1: Voice Accessibility**
- Support for various accents and speech patterns
- Clear visual feedback for hearing-impaired (live transcription)
- Adjustable voice speed for comprehension
- High-contrast mode for visual impairment

**NFR-A2: Mobile Accessibility**
- Touch targets minimum 44x44dp (WCAG compliant)
- Screen reader compatible (VoiceOver, TalkBack)
- Keyboard navigation support (for web PWA)
- Color contrast ratios meet WCAG AA standards

**NFR-A3: Language Clarity**
- Plain language in UI (no technical jargon)
- Clear error messages with actionable steps
- Onboarding suitable for non-technical users
- Content appropriate for reading level: Grade 8-10

### Reliability & Availability

**NFR-R1: System Uptime**
- Target: 99.5% uptime (MVP acceptable)
- Target: 99.9% uptime (production goal)
- Planned maintenance windows: off-peak hours only
- Maximum unplanned downtime: 4 hours per month

**NFR-R2: Error Handling**
- All user-facing errors have clear messages
- Automatic retry for transient failures
- Fallback experiences when voice pipeline fails
- Error tracking and alerting for engineering team

**NFR-R3: Data Backup & Recovery**
- User data backed up daily
- Conversation history backed up hourly
- Recovery Time Objective (RTO): 4 hours
- Recovery Point Objective (RPO): 1 hour

### Monitoring & Observability

**NFR-M1: Application Monitoring**
- Real-time dashboard for key metrics
- Track: concurrent users, conversation duration, error rates
- Alert engineering team for critical issues (>5% error rate)

**NFR-M2: Voice Quality Monitoring**
- Track: STT accuracy, TTS generation time, end-to-end latency
- User satisfaction surveys after conversations
- Monitor drop-off points in conversation flow

**NFR-M3: Cost Monitoring**
- Real-time API cost tracking per service
- Daily/weekly cost reports
- Alert when costs exceed budget thresholds
- Attribution: cost per conversation, cost per user

### Compliance & Legal

**NFR-C1: Age Restrictions**
- Minimum age: 13+ (COPPA compliance)
- Age verification during registration
- Parental consent for users under 18 (future consideration)

**NFR-C2: Terms of Service**
- Clear disclaimer: "for entertainment and guidance purposes"
- No medical, financial, or legal advice claims
- User agreement acceptance required
- Content moderation policy

---

## Implementation Planning

### Project Classification for Development

**Project Level:** 3 (Medium Complexity)
- Multiple integrated systems (voice pipeline, AI services, mobile app)
- Real-time communication requirements
- Third-party API orchestration
- Cross-platform mobile development

**Target Scale:** Medium (1,000-10,000 users MVP → 100,000+ growth)

**Development Approach:**
- Iterative sprints with user validation at each phase
- Beta testing crucial for voice UX validation
- Phased rollout: Web PWA first, Android second, iOS third

### Epic Breakdown Required

This PRD contains 6 major functional requirement areas + mobile platform requirements + voice pipeline integration. These must be decomposed into implementable epics and bite-sized stories (manageable within 200k context for dev agents).

**Suggested Epic Structure:**
1. **Voice Pipeline Setup** - Pipecat-ai + Daily.co + service integrations
2. **Numerology Engine** - Calculations + knowledge base
3. **User Management** - Auth, profiles, conversation history
4. **Mobile App Foundation** - React Native setup, UI framework, core screens
5. **Voice UX Implementation** - Mic handling, transcription, visual feedback
6. **Performance & Security** - Optimization, encryption, monitoring
7. **Testing & Deployment** - Beta testing, store compliance, launch

**Next Step:** Run `/bmad:bmm:workflows:create-epics-and-stories` to create the implementation breakdown.

---

## References

**Source Documents:**
- Product Brief: `/home/hieutt50/projects/numerologist-ai/docs/product-brief-numerologist-ai-2025-11-03.md`

**Technology Documentation:**
- React Native: https://reactnative.dev/
- Pipecat-ai: https://github.com/pipecat-ai/pipecat
- Daily.co: https://www.daily.co/
- Deepgram: https://deepgram.com/
- Azure OpenAI: https://azure.microsoft.com/en-us/products/ai-services/openai-service
- ElevenLabs: https://elevenlabs.io/

---

## Next Steps

### Immediate (Before Development):

1. **Epic & Story Breakdown** (Required)
   - Run: `/bmad:bmm:workflows:create-epics-and-stories`
   - Decomposes this PRD into implementable stories
   - Creates development roadmap

2. **Architecture Design** (Highly Recommended)
   - Run: `/bmad:bmm:workflows:architecture`
   - Define technical architecture decisions
   - Document system design for voice pipeline
   - Establish patterns for React Native + backend

3. **UX Design** (Optional but valuable)
   - Run: `/bmad:bmm:workflows:create-ux-design`
   - Create detailed UI mockups
   - Design conversation flows visually
   - Establish design system

### Development Phase:

4. **Sprint Planning** - Break epics into sprints
5. **Technical Spike** - Prove out voice pipeline (Pipecat-ai + services)
6. **Iterative Development** - Build, test, validate with users
7. **Beta Testing** - 50+ users for voice UX validation

---

## Product Magic - Captured Throughout

**The essence of Numerologist AI:**

Natural voice conversations with an AI numerology expert make ancient wisdom accessible to modern users. The magic happens when someone realizes they're having a real conversation about their life - asking follow-up questions, getting personalized insights, feeling understood - all through voice.

**This magic is woven throughout the PRD:**
- Vision: Voice-first accessibility (FR-1, UX Principles)
- Success: Measured by conversation depth and user delight
- Scope: Every MVP feature serves the natural conversation experience
- Innovation: First voice-only spiritual guidance platform
- Requirements: Natural conversation prioritized in every functional requirement
- NFRs: Performance targets ensure conversation feels natural (<3s latency)

**What users will say:** "It felt like talking to a real numerologist. I can't believe it remembered our last conversation!"

---

_This PRD captures the complete vision and requirements for Numerologist AI._

_Created through collaborative discovery between Hieu and AI facilitator (2025-11-03)._

_Ready for epic breakdown and implementation planning._
