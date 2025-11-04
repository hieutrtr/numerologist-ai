# Story 1.3: Setup Frontend with Expo TypeScript

**Status:** drafted

**Story ID:** 1.3

**Epic:** 1 - Foundation & Project Setup

---

## Story

**As a** frontend developer,
**I want** a React Native Expo app with TypeScript configured,
**so that** I can start building mobile UI with type safety.

---

## Acceptance Criteria

1. `mobile/` folder initialized with Expo TypeScript template
2. `src/` folder created with structure: `app/`, `components/`, `services/`, `stores/`, `types/`, `constants/`, `utils/`
3. `package.json` includes Expo SDK, React Native, TypeScript
4. `tsconfig.json` properly configured
5. Basic app structure with Expo Router
6. `npm install` completes successfully
7. `npm start` launches Expo dev server
8. App opens in browser (press 'w') showing "Numerologist AI" home screen
9. Hot reload works when editing code

---

## Tasks / Subtasks

- [ ] **Task 1: Initialize Expo project with TypeScript** (AC: #1, #3)
  - [ ] Navigate to mobile directory
  - [ ] Run `npx create-expo-app@latest . --template blank-typescript`
  - [ ] Verify `package.json` is created with Expo SDK, React Native, TypeScript
  - [ ] Verify `tsconfig.json` is generated

- [ ] **Task 2: Create source folder structure** (AC: #2)
  - [ ] Create `src/` directory inside mobile/
  - [ ] Create `src/app/` directory (Expo Router pages)
  - [ ] Create `src/components/` directory (UI components)
  - [ ] Create `src/services/` directory (API clients, utilities)
  - [ ] Create `src/stores/` directory (Zustand state stores)
  - [ ] Create `src/types/` directory (TypeScript type definitions)
  - [ ] Create `src/constants/` directory (App constants)
  - [ ] Create `src/utils/` directory (Helper functions)

- [ ] **Task 3: Configure TypeScript path aliases** (AC: #4)
  - [ ] Update `tsconfig.json` with path aliases for cleaner imports
  - [ ] Configure `@/*` to resolve to `./src/*`
  - [ ] Verify imports work: `import { Component } from '@/components/Component'`

- [ ] **Task 4: Configure Expo Router** (AC: #5)
  - [ ] Update `app.json` to enable typed routes
  - [ ] Set `experiments.typedRoutes: true` in Expo config
  - [ ] Create initial home screen in `src/app/index.tsx`
  - [ ] Display "Numerologist AI" title on home screen
  - [ ] Verify Expo Router discovers `src/app` directory

- [ ] **Task 5: Install dependencies** (AC: #6)
  - [ ] Run `npm install` in mobile directory
  - [ ] Verify all dependencies are installed without errors
  - [ ] Install additional packages: axios, zustand, @react-native-async-storage/async-storage, expo-secure-store
  - [ ] Verify `node_modules/` is created

- [ ] **Task 6: Test Expo dev server** (AC: #7, #8, #9)
  - [ ] Start dev server with `npm start`
  - [ ] Verify Expo dev server launches successfully
  - [ ] Press 'w' to open in browser
  - [ ] Verify home screen displays "Numerologist AI"
  - [ ] Test hot reload by editing component
  - [ ] Verify changes appear instantly without full reload

- [ ] **Task 7: Commit to Git** (Supporting)
  - [ ] Stage mobile/ directory and story files
  - [ ] Create commit with message: "Story 1.3: Setup Frontend with Expo TypeScript"
  - [ ] Verify commit is added to git history

---

## Dev Notes

### Requirements Context Summary

From Epic 1, Story 1.3:

**Core Requirements:**
- React Native frontend using Expo (rapid development, cross-platform)
- TypeScript for type safety in frontend code
- Structured folder organization following conventions (src/ with app/, components/, services/, stores/)
- Expo Router for file-based routing (similar to Next.js)
- Path aliases (@/) for cleaner imports across project
- Hot reload working for fast development feedback

**Why This Approach:**
- Expo: Official React Native tooling, handles Android/iOS/Web compilation
- TypeScript: Matches backend language capability for consistency
- Structured layout: Enables large team development with clear boundaries
- Router: Navigation framework built on file system structure
- Services layer: Separation of concerns for API communication, utilities

**Technical Constraints:**
- Node.js + npm ecosystem for frontend (vs Python uv for backend)
- TypeScript compilation required before runtime
- Expo CLI handles all build/bundling (no ejection to native code needed for this epic)

Source: [docs/epics.md#Story-1.3-Setup-Frontend-with-Expo-TypeScript]

### Project Structure Notes

**Target Structure After This Story:**

```
numerologist-ai/
├── backend/                          # Completed in Story 1.2
│   ├── pyproject.toml
│   ├── src/
│   │   ├── main.py
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   └── services/
│   └── ...
├── mobile/                           # ← This story creates and populates
│   ├── src/
│   │   ├── app/                      # Expo Router pages (file-based routing)
│   │   │   └── index.tsx             # Home screen
│   │   ├── components/               # Reusable UI components
│   │   ├── services/                 # API client, utilities
│   │   ├── stores/                   # Zustand state management
│   │   ├── types/                    # TypeScript types/interfaces
│   │   ├── constants/                # Constants (colors, strings, etc)
│   │   └── utils/                    # Helper functions
│   ├── package.json                  # npm dependencies
│   ├── tsconfig.json                 # TypeScript configuration
│   ├── app.json                      # Expo app configuration
│   └── .expo/                        # Expo cache
└── Makefile                          # Commands reference
```

**Key Files Created:**
- `mobile/package.json` - Defines dependencies (expo, react, typescript, axios, zustand, etc.)
- `mobile/tsconfig.json` - TypeScript compiler options with path aliases
- `mobile/app.json` - Expo app metadata and configuration
- `mobile/src/app/index.tsx` - Home screen component
- `mobile/src/services/api.ts` - Axios API client (prepared for Story 1.6)

**Structure Alignment:**
- Matches backend `src/` pattern for consistency across monorepo
- Follows React Native community conventions
- Path aliases (`@/`) enable module-like imports without relative paths
- Services and stores separate business logic from UI components

Source: [docs/epics.md#Story-1.3-Technical-Notes]

### Architecture Context

**Dependencies Explanation:**

| Package | Version | Purpose | Used In |
|---------|---------|---------|---------|
| `expo` | Latest | React Native framework with managed build | All stories |
| `react-native` | Latest | Mobile UI framework | UI components |
| `typescript` | Latest | Type safety for JavaScript | All code |
| `@react-navigation/native` | Via expo-router | File-based routing | Navigation |
| `axios` | Latest | HTTP client (matches backend API calls) | Story 1.6 |
| `zustand` | Latest | State management (small, fast) | Story 2.6 |
| `@react-native-async-storage/async-storage` | Latest | Persist non-sensitive data | Story 2.6 |
| `expo-secure-store` | Latest | Secure token storage | Story 2.6 |

**Expo Router Benefits:**
- File-based routing (like Next.js) - `src/app/index.tsx` → Home page
- Type-safe route navigation with TypeScript
- Built-in deep linking support
- Native navigation feel on iOS/Android
- Web support for PWA deployment (Story 8.6)

Source: [docs/epics.md#Story-1.3-Key-Dependencies-to-add], [docs/architecture.md]

### Testing Strategy

**Manual Verification:**

1. **Project Initialization:**
   - Directory check: `ls -la mobile/src/app` shows at least `index.tsx`
   - Package.json exists: `test -f mobile/package.json && echo "✓"`
   - TypeScript config exists: `test -f mobile/tsconfig.json && echo "✓"`

2. **Dependency Installation:**
   - `npm list expo` shows installed version
   - `npm list typescript` shows TypeScript is available
   - `npm list axios zustand` shows optional packages installed

3. **Expo Dev Server:**
   - Start: `cd mobile && npm start` (should show QR code)
   - Press 'w' key to open in browser
   - Wait 10-15 seconds for Metro bundler to compile
   - Browser shows Expo app interface

4. **App Functionality:**
   - Home screen displays "Numerologist AI" title
   - Hot reload: Edit `src/app/index.tsx`, save, observe instant update
   - No full page refresh required (indicates hot reload working)
   - Console shows no TypeScript errors

5. **Import Path Aliases:**
   - Create test file: `src/utils/test.ts` with `export const test = () => {}`
   - Import in component: `import { test } from '@/utils/test'`
   - Verify TypeScript resolves correctly (no red squiggles in IDE)

**Future Testing (Stories 2+):**
- Integration tests with Jest for components
- API integration tests with mock backend
- End-to-end tests with Detox framework
- TypeScript strict mode validation

Source: [docs/architecture.md#Frontend-Architecture]

---

## Dev Notes - Learnings from Previous Story

### From Story 1.2 (Status: done)

**Successful Patterns Established:**
- Backend infrastructure is running and tested (FastAPI on localhost:8000)
- uv package manager provides fast, reliable dependency management
- `/health` endpoint available for frontend integration testing
- Monorepo structure with clear backend/ and mobile/ separation maintained

**Key Takeaways for This Story:**
- Frontend (npm/React Native) and backend (uv/Python) are separate ecosystems
- Different package managers: backend uses `uv`, frontend uses `npm`
- Both will coordinate through HTTP/REST API (test in Story 1.6)
- Makefile supports both: `make backend` and `make mobile`

**Cross-Project Dependencies:**
- Story 1.3 (frontend setup) doesn't depend on Story 1.2 code, only that backend folder exists
- Story 1.5 (backend database) doesn't depend on frontend
- Story 1.6 (frontend → backend integration) is where cross-cutting concerns meet
- Stories can be developed in parallel: backend dev works on 1.5 while frontend dev works on 1.3/1.4

**Recommended Pattern for This Story:**
- Follow same git commit structure: `Story 1.3: Setup Frontend with Expo TypeScript`
- Keep story documentation in sync with implementation
- Test each acceptance criterion individually before marking complete
- Use Makefile to coordinate: `make mobile` for this story's testing

Source: [docs/stories/1-2-setup-backend-with-uv-fastapi.md#Dev-Agent-Record]

---

## Learnings from Previous Story

**From Story 1.2 (Status: done)**

**New Files/Patterns Created in Backend:**
- Backend infrastructure and FastAPI foundation solid
- uv.lock file ensures reproducible dependencies
- Startup/shutdown handlers for app lifecycle management
- Health check endpoint pattern established (`/health`)

**Architectural Decisions Made:**
- Monorepo approach allows parallel frontend/backend development
- Each tool ecosystem independent (uv for Python, npm for Node.js)
- Makefile provides unified dev workflow across languages

**Technical Debt:**
- None yet (Story 1.2 fully completed)

**For This Story:**
- Frontend needs same quality dependency management (package-lock.json in npm)
- Keep structure conventions consistent (src/ directory for source code)
- Prepare API service in Story 1.6 to call backend /health endpoint

Source: [docs/stories/1-2-setup-backend-with-uv-fastapi.md#Dev-Agent-Record]

---

## References

- **Epic Breakdown**: [Source: docs/epics.md#Story-1.3-Setup-Frontend-with-Expo-TypeScript]
- **Previous Story**: [Source: docs/stories/1-2-setup-backend-with-uv-fastapi.md#Dev-Agent-Record]
- **Architecture**: [Source: docs/architecture.md#Frontend-Architecture]
- **Expo Documentation**: [External: https://docs.expo.dev/]
- **React Native Documentation**: [External: https://reactnative.dev/]
- **TypeScript Handbook**: [External: https://www.typescriptlang.org/docs/]
- **Zustand Documentation**: [External: https://github.com/pmndrs/zustand]

---

## Dev Agent Record

### Context Reference

<!-- Path(s) to story context XML will be added here by context workflow -->

### Agent Model Used

Claude Haiku 4.5

### Debug Log References

### Completion Notes List

### File List

---

## Change Log

| Version | Date | Author | Notes |
|---------|------|--------|-------|
| 1.0 | 2025-11-04 | Claude (SM Agent) | Initial draft from Epic 1, Story 1.3 |
