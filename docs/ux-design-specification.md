# Numerologist AI - UX Design Specification

**Date:** 2025-11-07
**Version:** 1.0
**Project:** Numerologist AI
**Platform:** React Native (Mobile-first + Web)
**User Skill Level:** Intermediate

---

## Executive Summary

Numerologist AI delivers a **conversational voice experience** that feels like having a personal numerologist available 24/7. Users speak their questions, receive personalized insights, and can ask follow-up questions in natural conversation.

This UX specification defines how users interact with that magic, guided by three core principles:
- **Connected & Guided** - Users feel understood and supported
- **Content-First** - Insights and conversation history are visible and valued
- **Luxurious** - Premium gold aesthetic conveys spiritual wisdom and exclusivity

---

## Design Direction Summary

### Chosen Visual Direction: **Celestial Gold**

**Color Strategy:**
- **Primary:** #d4af37 (Gold) - Actions, highlights, guidance
- **Secondary:** #8b5cf6 (Purple) - Accents, mystical energy
- **Success:** #5eead4 (Teal) - Positive outcomes, insights
- **Background (Dark):** #0d0d1a - Deep, focused, meditative
- **Background (Light):** #1a1a33 - Card surfaces, content areas
- **Text (Primary):** #fef3c7 (Pale gold) - Main copy
- **Text (Muted):** #a8960b (Darker gold) - Secondary information

**Rationale:** Gold as primary conveys luxury, divine guidance, and spiritual wisdom. Purple accents add mystery and balance. The combination feels premium and trustworthy - essential for a wellness app.

### Chosen Layout Direction: **Content First**

**Philosophy:** Prioritize the conversation and insights above the record button. Users see:
1. Their past questions (conversation history)
2. AI responses and insights
3. Record button is always accessible (bottom) for follow-up questions

**Why This Works:**
- Users can review and reflect on insights (spiritual practice)
- Shows depth of conversation (engagement signal)
- Natural flow: read insights → ask follow-up → read new insights
- Balances voice-first with content-rich experience

---

## Core User Experience Flows

### Flow 1: Starting a New Conversation

**Entry Point:** Home screen with bottom navigation

**User Journey:**
```
1. User opens app → Home screen (empty state)
2. Sees: "Welcome back" + Recent readings (if any)
3. Large record button at bottom prompts action
4. Taps record button → Enters "recording state"
5. Says their question
6. Releases button → API call to backend
7. See: Loading state with animated waveform
8. AI response appears in conversation stream
9. Can ask follow-up questions by tapping record again
```

**Visual States:**
- **Empty State:** "No readings yet. Ask your first question about numerology"
- **Recording:** Animated waveform, "Listening..." text, large pulsing record button
- **Processing:** Skeleton loader with "AI is thinking..." message
- **Response:** Insight appears with fade-in animation, user can immediately ask follow-up

**Key Interactions:**
- Record button is always visible and prominent
- Users can swipe up from record button to see full conversation history
- Voice feedback: soft chime when recording starts/stops
- Haptic feedback on button press (if available)

---

### Flow 2: Following Up with Questions

**Trigger:** User sees an insight and wants to explore deeper

**User Journey:**
```
1. User reads AI's insight in conversation
2. Taps record button to ask follow-up
3. Speaks their next question
4. AI responds in conversation stream
5. Conversation builds naturally
```

**Visual Experience:**
- User messages appear right-aligned in purple-tinted cards
- AI responses appear left-aligned in gold-accented cards
- Each new message animated in smoothly
- Timestamp shows when insights were received
- User can swipe to see full message if truncated

**Key Feature:** Progressive disclosure - full conversations visible by scrolling, newest at bottom

---

### Flow 3: Reviewing Past Readings

**Access via:** History tab (bottom navigation)

**User Journey:**
```
1. User taps History tab
2. Sees list of past conversations (reverse chronological)
3. Each card shows: Date, first question, preview of insights, life path number if calculated
4. Taps a conversation to expand and review full flow
5. Can re-ask questions or start new conversation
```

**Visual Experience:**
- Card-based layout for each conversation
- Gold accents show key insights (life path number highlighted)
- Quick actions: "Continue Conversation" button on each card
- Search/filter by date or theme (future enhancement)

---

## Visual Design System

### Typography

**Font Stack:** `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`

**Type Scale:**
- **Display:** 32px, 700 weight (screen titles)
- **Heading 1:** 24px, 700 weight (section headers)
- **Heading 2:** 18px, 600 weight (card titles)
- **Body:** 16px, 400 weight (message text)
- **Small:** 14px, 400 weight (timestamps, labels)
- **Tiny:** 12px, 400 weight (captions, hints)

**Color Application:**
- Primary text: #fef3c7 (pale gold) on dark backgrounds
- Secondary text: #a8960b (darker gold) for metadata
- Accent text: #8b5cf6 (purple) for interactive elements
- Success text: #5eead4 (teal) for positive outcomes

### Spacing System

**Base Unit:** 8px (Multiples: 8, 16, 24, 32, 40, 48, 64, 80, 96)

**Application:**
- **Padding:** 16px (cards), 20px (screens), 12px (buttons)
- **Margin:** 24px (sections), 16px (cards), 8px (inline)
- **Gap (flexbox):** 8px (tight), 12px (normal), 16px (loose)

### Layout Grid

**Mobile (Primary):**
- Single column, full width minus 20px padding
- Safe area: top (status bar), bottom (navigation)
- Record button: 120px diameter, centered, 20px from bottom nav

**Web (Secondary):**
- Max-width: 600px (maintains mobile-optimized proportions)
- Can expand to 2-column at larger breakpoints (future)
- Responsive breakpoints: 375px, 768px, 1024px

### Component Library Strategy

**Using:** Design System (to be specified in Phase 2)

**Core Components Needed:**
1. **Record Button** - Custom component
   - Large, circular, gold primary color
   - Pulsing animation when recording
   - Ripple effect on press
   - States: ready, recording, processing, disabled

2. **Message Card** - Custom component
   - User message (purple-tinted, right-aligned)
   - AI message (gold-accented, left-aligned)
   - Timestamp
   - Copy action on long-press

3. **Insight Card** - Custom component
   - Life Path number display (large, gold)
   - Insight text
   - Key terms highlighted
   - "More context" expandable section

4. **Conversation History List** - Custom component
   - Date grouping
   - Quick preview
   - "Continue" action

5. **Loading State** - Custom component
   - Animated waveform
   - "AI is thinking..." message
   - Skeleton loaders for message preview

---

## UX Pattern Decisions

### Button Hierarchy

**Primary Actions (Gold #d4af37):**
- Record new question
- Continue conversation
- Start first reading
- Submit profile info

**Secondary Actions (Purple #8b5cf6):**
- View history
- Share insights
- Settings
- Help

**Tertiary Actions (Text links):**
- Copy message
- Delete history item
- Learn more

**Destructive Actions (Red #ef4444):**
- Clear all history
- Delete account

### Feedback Patterns

**Success:** Animated checkmark + subtle fade-in of response
**Error:** Red inline message with retry button
**Loading:** Animated waveform + "AI is thinking..." message
**Empty State:** Friendly message with illustration + CTA

### Form & Input Patterns

**Recording Input:** Voice-first, no text typing
**Future Enhancement:** Optional text input for users who prefer typing

**Validation:**
- Instant: Audio detected (visual feedback)
- On complete: Transcription shown below record button
- On error: "Couldn't hear you clearly. Try again?" with retry

### Navigation Patterns

**Bottom Tab Navigation (Mobile-First):**
- **Home (🎙️):** New readings, recent conversations
- **History (📚):** Past conversations, search/filter
- **Profile (👤):** User info, preferences, help

**Active State:** Gold highlight + filled icon

**Web Navigation:** Same tabs, positioned at bottom or side depending on breakpoint

### Modal & Dialog Patterns

**Confirmation Dialogs:** Purple overlay, centered dialog, gold action buttons
**Settings:** Slide-up panel from bottom (mobile), modal (web)
**Help/Tips:** Toast notifications (temporary info), expandable help sections

### Empty State Patterns

**No Conversations Yet:**
- Friendly illustration (spiritual, gold-themed)
- "Ask your first question about numerology"
- Large, obvious record button

**No Internet:**
- Offline message
- "We'll sync when you're online"
- Can review cached conversations

**No Results (Search/Filter):**
- "No conversations found"
- "Try different search terms"
- "Or start a new conversation"

### Notification Patterns

**Toasts (Bottom, auto-dismiss after 3s):**
- Success: Green border, gold text
- Error: Red border, white text
- Info: Blue border, gold text

**Persistent Notifications:**
- Important updates: Purple banner at top
- Profile incomplete: Gold banner "Complete profile for better insights"

### Confirmation Patterns

**Destructive Actions Require Confirmation:**
- Delete conversation: "Delete this conversation? You can't undo this."
- Clear all history: "Delete all {{count}} conversations?"
- Delete account: Requires email confirmation

**Non-destructive Can Be Undone:**
- Hide conversation: "Removed from view. Undo?" (15-second window)

---

## Responsive Design Strategy

### Mobile (375px - Primary)

**Full-screen experience, vertical orientation**
- Single column layout
- Bottom navigation always visible
- Record button floats above nav
- Messages scroll vertically
- Landscape blocked (portrait only recommended)

### Tablet (768px - Secondary)

**Can support 2-column layout**
- Left column: Conversation history (always visible)
- Right column: Current reading or detail view
- Horizontal orientation supported
- Larger touch targets (48px minimum)

### Web (1024px+)

**Desktop-optimized but similar to tablet**
- Max-width: 900px (maintains focus)
- Can add sidebar for history
- Record button prominent but not floating
- Keyboard shortcuts (future enhancement)

### Layout Adaptation Rules

- **Text:** Scales with viewport, min 16px
- **Buttons:** Min 48px height (touch target), 44px minimum width
- **Cards:** Full-width minus padding on mobile, max-width on larger screens
- **Messages:** Max 80% width with proper margins

---

## Accessibility Strategy

**Target:** WCAG 2.1 Level AA

### Key Requirements

**Color Contrast:**
- Text vs background: 4.5:1 minimum (gold on dark: ✓ 7.2:1)
- UI elements: 3:1 minimum

**Keyboard Navigation:**
- All interactive elements accessible via Tab key
- Record button: Tab + Space to activate
- Tab order: logical (top to bottom, left to right)

**Screen Reader Support:**
- Record button: "Record question, double-tap to start recording"
- Messages: "User said [text]" vs "Numerologist responded [text]"
- Timestamps: "15 minutes ago" (relative, friendly)
- Loading: "Loading response..."

**Voice/Audio Considerations:**
- Transcription always shown (captions)
- Option to mute notifications
- Clear audio feedback cues (not just visual)
- Haptic feedback for haptic-enabled devices

**Focus Indicators:**
- Visible focus ring (gold) on all interactive elements
- 3px minimum focus ring width
- Clear, high-contrast focus states

**Touch Targets:**
- Minimum 48px × 48px
- Record button: 120px × 120px (far exceeds minimum)
- Navigation items: 48px height × equal width

---

## Visual Design Principles

### 1. **Conversation as Hero**
The conversation history is the main attraction. Users came for insights, so insights should be prominent and beautiful.

### 2. **Record Button Always Ready**
The record button is never hidden, never more than one tap away. It should feel inviting and easy to use.

### 3. **Gold Conveys Guidance**
Gold is used deliberately for important elements (record button, insight highlights, success states) to communicate divine guidance and wisdom.

### 4. **Calm, Dark Aesthetic**
Dark backgrounds reduce eye strain during evening use and create a meditative, focused atmosphere perfect for spiritual reflection.

### 5. **Spacious, Breathing Layout**
Generous whitespace (dark space in dark theme) prevents cognitive overload. Users can focus on the conversation without distraction.

### 6. **Smooth, Intentional Motion**
Every animation has purpose:
- Waveform animates to show "listening"
- Messages fade in as they arrive
- Record button pulses gently when active

### 7. **Premium, Not Playful**
Gold accents and careful spacing convey luxury and trust. Animations are subtle, not bouncy. This is a spiritual tool, not a game.

---

## Mobile Experience Specifics

### Portrait Orientation (Primary)

**Screen Heights Optimized For:**
- iPhone 12/13/14 (390×844) - Standard reference
- iPhone SE (375×667) - Minimum height
- Pixel 6 (412×915) - Android reference

**Safe Areas Respected:**
- Top: Status bar (24px) + notch clearance
- Bottom: Navigation bar (83px total with safe area)

### Recording Experience

**Visual Feedback During Recording:**
1. Record button pulses with gold glow
2. Animated waveform shows audio input
3. Transcription appears in real-time below waveform
4. User can see what's being captured (confidence)

**Stop Recording:**
- Release button automatically
- Or tap button again to stop
- Clear visual confirmation: "Sent ✓"

### Conversation Scrolling

**Behavior:**
- Auto-scroll to new messages
- User can scroll up to review history
- Smooth scroll, no jumps
- Sticky timestamp headers (future)

---

## Web Experience Specifics (Future Phase)

### Desktop Behavior

**Considerations:**
- Mouse hover states (not relevant for mobile)
- Keyboard shortcuts (Spacebar to record? CTRL+K for search?)
- Larger screen real estate can show more context
- Can add sidebar for navigation

**Recommended:** Keep desktop close to mobile experience initially (mobile-first approach)

---

## Interaction Patterns Summary

| Interaction | Trigger | Feedback | Result |
|-------------|---------|----------|--------|
| Start recording | Tap record button | Button glows, waveform animates | Speech recognition begins |
| Stop recording | Release button (or tap again) | Fade to loading state | Transcription sent to backend |
| Submit question | Auto on release | "Sent ✓" check | Processing spinner appears |
| Receive insight | Backend responds | Message fades in | User can read and ask follow-up |
| Ask follow-up | Tap record again | Same as initial | Continue conversation |
| View history | Tap History tab | Slide transition | List of past conversations |
| Delete conversation | Long-press + confirm | Fade out + undo toast | Removed (temporarily) |
| Submit profile | Tap Save | Success toast | Navigate back |

---

## Design System Components - Future Specification

The following custom components will be implemented in development phase:

1. **RecordButton** - Animated, primary CTA
2. **MessageCard** - User/AI message display
3. **InsightCard** - Highlighted numerology insights
4. **LoadingWaveform** - Audio processing animation
5. **ConversationList** - History display
6. **ConfirmDialog** - Destructive action confirmation
7. **EmptyState** - First-run and no-data states
8. **Toast** - Temporary notifications
9. **NavigationTabs** - Bottom navigation
10. **AudioTranscription** - Real-time transcription display

---

## Design Tokens (For Development)

```yaml
colors:
  primary: "#d4af37"
  primary_dark: "#a8960b"
  secondary: "#8b5cf6"
  accent: "#5eead4"
  success: "#5eead4"
  warning: "#fbbf24"
  error: "#ef4444"

  background:
    dark: "#0d0d1a"
    light: "#1a1a33"

  text:
    primary: "#fef3c7"
    secondary: "#a8960b"
    muted: "#6b7280"

spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  xxl: 48px

typography:
  font_family: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
  sizes:
    display: 32px
    h1: 24px
    h2: 18px
    body: 16px
    small: 14px
    tiny: 12px

breakpoints:
  mobile: 375px
  tablet: 768px
  desktop: 1024px
```

---

## Next Steps

### Phase 2: High-Fidelity Design
- Create Figma/Sketch design system components
- Design screens for all major user flows
- Create interactive prototype
- User testing with target audience

### Phase 3: Development Handoff
- Component library implementation
- CSS-in-JS or Tailwind configuration
- Animation specifications
- Accessibility implementation

### Phase 4: Post-Launch
- User testing and feedback
- Refinements based on analytics
- Dark mode toggle (if not default dark)
- Accessibility audit

---

## Approval & Signoff

**Design Direction:** Celestial Gold + Content First
**Primary Color:** Gold (#d4af37)
**Secondary Color:** Purple (#8b5cf6)
**Layout:** Content-first (history visible, record button always accessible)
**Platform Priority:** Mobile-first (React Native) with web support
**Accessibility Target:** WCAG 2.1 Level AA

**Approved By:** [User Name]
**Approved Date:** [Date]
**Version:** 1.0

---

## Appendix: Inspiration References

**Audio-First Design:** Spotify's now-playing interface
**Wellness Aesthetic:** Calm, Apple Health
**Voice Interaction:** ChatGPT's natural conversation
**Luxury Aesthetic:** Figma's dark theme with gold accents
**Spiritual Design:** Calm app's meditative visual language

---

**Document Status:** FINAL - Ready for Design System Development
