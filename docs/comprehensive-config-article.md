# The Complete Guide to Configuring React Native with NativeWind
## For Developers Building with AI - Understanding What Actually Happens

**For**: Backend developers, ML engineers, DevOps, and vibe coders building mobile apps
**Why**: So you can work effectively with AI coding assistants like Claude Code and Cursor
**Goal**: Understand configuration fundamentals to debug when AI gets stuck

---

## Why This Guide Exists

You're using AI to build your mobile app. It writes code fast. But then you hit errors like:

```
❌ Module not found: nativewind
❌ className prop not recognized
❌ Styles not applying after config changes
❌ Metro bundler stuck
```

**The problem**: AI tools are amazing at writing business logic, but they struggle with **configuration context**. Why? Because configuration requires understanding how **multiple tools interact** - something that's often scattered across different documentation sites.

This guide bridges that gap. After reading this, you'll understand:
1. What each config file does
2. How they work together
3. Where to look when things break
4. How to explain problems to AI effectively

---

## Table of Contents

1. [The Big Picture: What Are We Building?](#the-big-picture)
2. [The Five Config Files You Need](#the-five-config-files)
3. [How They Work Together (The Pipeline)](#the-pipeline)
4. [Step-by-Step Setup](#step-by-step-setup)
5. [Common Errors & Solutions](#common-errors)
6. [Working with AI: Best Practices](#working-with-ai)
7. [Debugging Checklist](#debugging-checklist)

---

## The Big Picture: What Are We Building? {#the-big-picture}

### Traditional React Native Styling (Without NativeWind)

```tsx
import { StyleSheet } from 'react-native';

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#007AFF',
    padding: 16,
    borderRadius: 8,
  },
  text: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: 'bold',
  }
});

<View style={styles.container}>
  <Text style={styles.text}>Hello World</Text>
</View>
```

**Problems**:
- Lots of boilerplate (`StyleSheet.create`)
- No design system (colors/spacing scattered everywhere)
- Hard to maintain (change primary color = find/replace across 50 files)

### With NativeWind (Tailwind CSS for React Native)

```tsx
<View className="bg-primary p-4 rounded-lg">
  <Text className="text-white text-lg font-bold">Hello World</Text>
</View>
```

**Benefits**:
- No `StyleSheet.create` boilerplate
- Design system in one file (`tailwind.config.js`)
- Familiar Tailwind syntax
- Type-safe with autocomplete

**The catch**: Requires proper configuration! That's what this guide is about.

---

## The Five Config Files You Need {#the-five-config-files}

Think of these as a **pipeline**. Each file has a specific job, and they must work together.

### Quick Reference

| File | Purpose | When You Edit It |
|------|---------|------------------|
| `package.json` | Dependencies | Adding new packages |
| `babel.config.js` | Code transformation | Rarely (set once) |
| `metro.config.js` | Bundler setup | Rarely (set once) |
| `tailwind.config.js` | Design system | Often (colors, spacing) |
| `postcss.config.js` | CSS processing | Rarely (set once) |
| `global.css` | Tailwind entry | Rarely (set once) |

Let's understand each one.

---

### 1. `package.json` - The Dependencies Manifest

**What it is**: Lists all the libraries your app needs.

**Required for NativeWind**:

```json
{
  "dependencies": {
    "expo": "~51.0.0",
    "react-native": "0.74.0",
    "nativewind": "^4.2.1",
    "tailwindcss": "^3.4.18",
    "react-native-reanimated": "~3.10.0"
  },
  "devDependencies": {
    "autoprefixer": "^10.4.21",
    "postcss": "^8.5.6"
  }
}
```

**Key packages explained**:

- **`nativewind`**: The bridge between Tailwind CSS and React Native
- **`tailwindcss`**: The utility-class CSS framework
- **`postcss`**: Processes CSS files (Tailwind needs this)
- **`autoprefixer`**: Adds browser compatibility (included with PostCSS)
- **`react-native-reanimated`**: For smooth animations (NativeWind uses it)

**When AI messes up**: It might forget `postcss` or use wrong versions. Check package versions match the official NativeWind docs.

---

### 2. `babel.config.js` - The Code Transformer

**What it does**: Transforms your modern JavaScript/TypeScript/JSX into code React Native understands.

**Why NativeWind needs it**: To make `className` props work in React Native.

**The correct configuration**:

```javascript
module.exports = function (api) {
  api.cache(true);
  return {
    presets: [
      // ⚠️ ORDER MATTERS!
      ["babel-preset-expo", { jsxImportSource: "nativewind" }],
      "nativewind/babel",
    ],
    plugins: [
      // ⚠️ THIS MUST BE LAST!
      "react-native-reanimated/plugin",
    ],
  };
};
```

**Critical details**:

1. **`jsxImportSource: "nativewind"`**: Changes how JSX is compiled
   - Without this: `className` props are ignored
   - With this: `className` props work like magic

2. **`"nativewind/babel"`**: NativeWind's Babel preset
   - Processes Tailwind classes
   - Converts them to React Native styles

3. **`react-native-reanimated/plugin`**: Animation support
   - **MUST be last** in the plugins array
   - If not last: Animations break mysteriously

**Common error**:
```
❌ className prop not recognized
```
**Fix**: Check `jsxImportSource: "nativewind"` is present.

---

### 3. `metro.config.js` - The Bundler Configuration

**What Metro is**: Metro is React Native's JavaScript bundler (like Webpack for React Native).

**What it does**:
1. Bundles all your `.js/.tsx` files into one bundle
2. Processes assets (images, fonts)
3. Handles hot reloading

**Why NativeWind needs it**: To process CSS files.

**The correct configuration**:

```javascript
const { getDefaultConfig } = require('expo/metro-config');
const { withNativeWind } = require('nativewind/metro');

const config = getDefaultConfig(__dirname);

// ⚠️ THIS IS THE KEY LINE
module.exports = withNativeWind(config, { input: './global.css' });
```

**What this does**:

1. `getDefaultConfig(__dirname)`: Gets Expo's default Metro config
2. `withNativeWind(config, { input: './global.css' })`: Wraps config to:
   - Read `global.css`
   - Process it with PostCSS and Tailwind
   - Make Tailwind classes available in your app

**Visual flow**:

```
Metro reads global.css
    ↓
Sends to PostCSS
    ↓
PostCSS runs Tailwind plugin
    ↓
Tailwind generates utility classes
    ↓
NativeWind makes them available as className props
```

**Common errors**:

```
❌ Cannot find module './global.css'
```
**Fix**: Make sure `global.css` exists at project root.

```
❌ withNativeWind is not a function
```
**Fix**: Run `npm install nativewind`

---

### 4. `tailwind.config.js` - Your Design System

**What it is**: The single source of truth for all your design tokens (colors, spacing, fonts).

**This is where you customize everything**.

**Basic structure**:

```javascript
module.exports = {
  // ⚠️ CRITICAL: Files to scan for class names
  content: [
    './App.{js,jsx,ts,tsx}',
    './src/**/*.{js,jsx,ts,tsx}',
  ],

  // React Native compatibility
  presets: [require('nativewind/preset')],

  // Your design system
  theme: {
    extend: {
      colors: {
        primary: '#007AFF',
        secondary: '#5856D6',
        danger: '#FF3B30',
      },
      spacing: {
        xs: '4px',
        sm: '8px',
        md: '16px',
        lg: '24px',
      },
      fontSize: {
        xs: '12px',
        sm: '14px',
        base: '16px',
        lg: '18px',
        xl: '20px',
      }
    },
  },
};
```

**Key sections explained**:

#### `content` Array
```javascript
content: ['./src/**/*.{js,jsx,ts,tsx}']
```

**What it does**: Tells Tailwind which files to scan for class names.

**Why it matters**:
- Tailwind scans these files
- Finds class names like `bg-primary`, `p-4`
- Generates CSS **only** for classes you actually use
- Unused classes = not generated = smaller bundle

**Example**:
```tsx
// You write this in src/screens/Home.tsx
<View className="bg-primary p-4" />

// Tailwind scans src/screens/Home.tsx (matches pattern)
// Finds: bg-primary, p-4
// Generates CSS for those classes
// Ignores: bg-secondary, p-8 (not used)
```

#### `presets`
```javascript
presets: [require('nativewind/preset')]
```

**What it does**: Loads NativeWind's preset configuration.

**Why needed**: Adapts Tailwind for React Native:
- Maps CSS properties → React Native StyleSheet properties
- Removes browser-specific features (hover, focus-visible, etc.)
- Handles platform differences (iOS vs Android)

**Example mapping**:
```
CSS                     →  React Native
background-color: red   →  backgroundColor: 'red'
padding-left: 16px      →  paddingLeft: 16
flex-direction: row     →  flexDirection: 'row'
```

#### `theme.extend`
```javascript
theme: {
  extend: {
    colors: { primary: '#007AFF' },
    spacing: { md: '16px' },
  }
}
```

**What it does**: Defines your design tokens.

**How to use**:

```javascript
// In tailwind.config.js
colors: {
  primary: '#007AFF',
  secondary: '#5856D6',
}
spacing: {
  xs: '4px',
  md: '16px',
}

// In your component
<View className="bg-primary p-md">
  <Text className="text-secondary">Hello</Text>
</View>

// Generates:
{
  backgroundColor: '#007AFF',
  padding: 16,
  color: '#5856D6'
}
```

**Common error**:

```
❌ Styles not applying after changing tailwind.config.js
```
**Fix**: Clear Metro cache
```bash
npm start -- --reset-cache
```

---

### 5. `postcss.config.js` - The CSS Processor

**What PostCSS is**: A tool that transforms CSS with plugins.

**Why we need it**: Tailwind is a PostCSS plugin.

**The correct configuration**:

```javascript
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
```

**What happens**:

```
Metro reads global.css
    ↓
PostCSS processes it
    ↓
Plugin 1: tailwindcss
  - Reads @tailwind directives
  - Generates utility classes
    ↓
Plugin 2: autoprefixer
  - Adds vendor prefixes (not really needed for RN)
    ↓
Result: All Tailwind classes available
```

**You rarely edit this file**. It's "set and forget."

---

### 6. `global.css` - The Tailwind Entry Point

**What it is**: The file that triggers Tailwind CSS generation.

**The complete file** (just 3 lines!):

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

**What each directive does**:

#### `@tailwind base;`
Generates reset/base styles (mostly for web, ignored in React Native).

#### `@tailwind components;`
Where you can define custom component classes:

```css
@layer components {
  .btn-primary {
    @apply bg-primary text-white px-4 py-2 rounded-lg;
  }
}
```

Usage:
```tsx
<TouchableOpacity className="btn-primary">
  <Text>Click Me</Text>
</TouchableOpacity>
```

#### `@tailwind utilities;` ⭐ Most important
Generates all the utility classes (`bg-*`, `text-*`, `p-*`, etc.)

**How it works**:

```
Metro sees: withNativeWind(config, { input: './global.css' })
    ↓
Reads global.css
    ↓
Sees @tailwind utilities
    ↓
Scans files in content array
    ↓
Finds class names: bg-primary, p-4, text-lg
    ↓
Looks up in tailwind.config.js:
  - bg-primary → colors.primary → '#007AFF'
  - p-4 → spacing[4] → 16px
  - text-lg → fontSize.lg → 18px
    ↓
Generates CSS for those classes
    ↓
NativeWind converts to React Native styles
```

**Common mistake**:

```tsx
// ❌ DON'T import global.css
import './global.css';  // WRONG!

// ✅ Metro processes it automatically
// Just use className
<View className="bg-primary" />
```

---

## How They Work Together (The Pipeline) {#the-pipeline}

### The Complete Flow

```
┌─────────────────────────────────────────────────┐
│  1. YOU WRITE CODE                              │
│  <View className="bg-primary p-4" />           │
└────────────────┬────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────┐
│  2. BABEL TRANSFORM (babel.config.js)          │
│  - Transforms JSX                               │
│  - Processes className (jsxImportSource)        │
│  - Enables NativeWind                           │
└────────────────┬────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────┐
│  3. METRO BUNDLER (metro.config.js)            │
│  - Bundles all files                            │
│  - Reads global.css (via withNativeWind)        │
│  - Sends to PostCSS                             │
└────────────────┬────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────┐
│  4. POSTCSS PROCESSING (postcss.config.js)     │
│  - Processes global.css                         │
│  - Runs Tailwind plugin                         │
└────────────────┬────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────┐
│  5. TAILWIND CSS (tailwind.config.js)          │
│  - Scans content files                          │
│  - Finds: bg-primary, p-4                       │
│  - Looks up colors.primary → '#007AFF'          │
│  - Looks up spacing[4] → 16                     │
│  - Generates CSS classes                        │
└────────────────┬────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────┐
│  6. NATIVEWIND RUNTIME                          │
│  - Receives generated CSS                       │
│  - Maps className → React Native styles         │
│  className="bg-primary p-4"                     │
│  → style={{ backgroundColor: '#007AFF',         │
│             padding: 16 }}                      │
└────────────────┬────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────┐
│  7. REACT NATIVE RENDERS                        │
│  <NativeView                                    │
│    style={{                                     │
│      backgroundColor: '#007AFF',                │
│      padding: 16                                │
│    }}                                           │
│  />                                             │
└─────────────────────────────────────────────────┘
```

### Key Insight

Each config file is a **step in the pipeline**. If one fails, the whole chain breaks.

**Example error chain**:

```
❌ Babel config wrong
  → className props not processed
    → Metro can't find NativeWind transform
      → Styles don't apply
        → App looks broken
```

---

## Step-by-Step Setup {#step-by-step-setup}

### Starting from Scratch

Follow these steps **in order**:

#### Step 1: Create Expo App

```bash
npx create-expo-app my-app
cd my-app
```

#### Step 2: Install Dependencies

```bash
npm install nativewind tailwindcss react-native-reanimated
npm install --save-dev postcss autoprefixer
```

#### Step 3: Create `tailwind.config.js`

```bash
npx tailwindcss init
```

Edit the generated file:

```javascript
module.exports = {
  content: [
    './App.{js,jsx,ts,tsx}',
    './src/**/*.{js,jsx,ts,tsx}',
  ],
  presets: [require('nativewind/preset')],
  theme: {
    extend: {
      colors: {
        primary: '#007AFF',
      },
    },
  },
};
```

#### Step 4: Create `postcss.config.js`

```javascript
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
```

#### Step 5: Create `global.css`

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

#### Step 6: Update `babel.config.js`

```javascript
module.exports = function (api) {
  api.cache(true);
  return {
    presets: [
      ["babel-preset-expo", { jsxImportSource: "nativewind" }],
      "nativewind/babel",
    ],
    plugins: [
      "react-native-reanimated/plugin",  // MUST BE LAST
    ],
  };
};
```

#### Step 7: Update `metro.config.js`

```javascript
const { getDefaultConfig } = require('expo/metro-config');
const { withNativeWind } = require('nativewind/metro');

const config = getDefaultConfig(__dirname);

module.exports = withNativeWind(config, { input: './global.css' });
```

#### Step 8: Create `nativewind-env.d.ts` (TypeScript only)

```typescript
/// <reference types="nativewind/types" />
```

#### Step 9: Test It

```tsx
// App.tsx
import { View, Text } from 'react-native';

export default function App() {
  return (
    <View className="flex-1 items-center justify-center bg-primary">
      <Text className="text-white text-2xl font-bold">
        Hello NativeWind!
      </Text>
    </View>
  );
}
```

#### Step 10: Run

```bash
npm start -- --reset-cache
```

Press `i` for iOS or `a` for Android.

---

## Common Errors & Solutions {#common-errors}

### Error 1: `className` prop not recognized

```
❌ Property 'className' does not exist on type 'ViewProps'
```

**Cause**: Babel not configured correctly.

**Solution checklist**:
1. Check `babel.config.js` has `jsxImportSource: "nativewind"`
2. Check `"nativewind/babel"` preset exists
3. Restart Metro: `npm start -- --reset-cache`
4. Check `nativewind-env.d.ts` exists (TypeScript)

---

### Error 2: Styles not applying

```
✅ No errors
❌ But styles don't show
```

**Cause**: Multiple possible reasons.

**Debugging steps**:

1. **Check Metro is processing `global.css`**:
   ```javascript
   // metro.config.js
   module.exports = withNativeWind(config, { input: './global.css' });
   ```

2. **Check `global.css` exists** at project root

3. **Check `content` in `tailwind.config.js`** matches your files:
   ```javascript
   content: [
     './App.{js,jsx,ts,tsx}',
     './src/**/*.{js,jsx,ts,tsx}',  // Does this match your structure?
   ]
   ```

4. **Clear Metro cache**:
   ```bash
   npm start -- --reset-cache
   ```

5. **Check class names are valid**:
   ```tsx
   // ✅ Correct
   <View className="bg-primary" />

   // ❌ Wrong (typo)
   <View className="bg-primray" />
   ```

---

### Error 3: Module not found errors

```
❌ Cannot find module 'nativewind/metro'
```

**Cause**: Dependencies not installed.

**Solution**:
```bash
# Delete node_modules and reinstall
rm -rf node_modules
npm install

# Or use clean install
npm ci
```

---

### Error 4: Tailwind config changes not applying

```
Changed colors in tailwind.config.js
❌ Old colors still showing
```

**Cause**: Metro cache.

**Solution**:
```bash
npm start -- --reset-cache
```

**Pro tip**: After changing ANY config file, always clear cache.

---

### Error 5: Reanimated plugin errors

```
❌ Worklet cannot be used...
```

**Cause**: `react-native-reanimated/plugin` not last.

**Solution**: Check `babel.config.js`:

```javascript
plugins: [
  "react-native-reanimated/plugin",  // ← MUST BE LAST
]
```

---

### Error 6: `global.css` not found

```
❌ Cannot find module './global.css'
```

**Causes**:
1. File doesn't exist
2. Wrong path in `metro.config.js`

**Solution**:

1. Check file exists:
   ```bash
   ls global.css  # Should exist at project root
   ```

2. Check path in Metro config:
   ```javascript
   // If global.css is at root
   withNativeWind(config, { input: './global.css' })

   // If in src folder
   withNativeWind(config, { input: './src/global.css' })
   ```

---

## Working with AI: Best Practices {#working-with-ai}

### When AI Gets Stuck

AI coding assistants (Claude Code, Cursor, etc.) are great but have limitations with configuration. Here's how to work with them effectively.

### Problem: AI Suggests Wrong Config

**Example**:
```
You: "Add NativeWind to my app"

AI: "Add this to metro.config.js:
module.exports = {
  transformer: {
    babelTransformerPath: require.resolve('nativewind/babel')
  }
}"
```

**This is WRONG for NativeWind v4!**

**How to fix**:

1. **Be specific about versions**:
   ```
   You: "Add NativeWind v4 to my Expo app using the withNativeWind wrapper"
   ```

2. **Reference official docs**:
   ```
   You: "Follow the setup from https://www.nativewind.dev/v4/getting-started/expo-router"
   ```

3. **Show your current config**:
   ```
   You: "Here's my current babel.config.js: [paste file]
   Add NativeWind v4 support to this config"
   ```

### Problem: AI Doesn't Clear Cache

**Example**:
```
You: "Styles still not working"

AI: "Try changing your tailwind config..."
```

AI often forgets to mention clearing Metro cache!

**Always add manually**:
```bash
npm start -- --reset-cache
```

### Problem: AI Mixes Versions

AI might mix NativeWind v2 and v4 syntax because it's trained on both.

**NativeWind v2** (old):
```javascript
// ❌ Don't use this anymore
const config = getDefaultConfig(__dirname);
config.transformer.babelTransformerPath = require.resolve('nativewind/babel');
```

**NativeWind v4** (current):
```javascript
// ✅ Use this
module.exports = withNativeWind(config, { input: './global.css' });
```

**How to avoid**:
```
You: "Use NativeWind v4 (the latest version with withNativeWind)"
```

### Effective Prompts for AI

**❌ Vague**:
```
"My styles aren't working"
```

**✅ Specific**:
```
"I'm using NativeWind v4 with Expo. Styles in my components don't apply.
Here's my metro.config.js: [paste]
Here's my babel.config.js: [paste]
I've cleared Metro cache with npm start -- --reset-cache
What am I missing?"
```

**❌ Vague**:
```
"Add dark mode"
```

**✅ Specific**:
```
"Add dark mode to my NativeWind v4 setup. I want to:
1. Add dark variants to tailwind.config.js
2. Toggle between light/dark themes
3. Use className='dark:bg-black' syntax
Show me the complete implementation"
```

### When to Debug Manually vs Ask AI

**Ask AI when**:
- Writing business logic
- Creating new components
- Refactoring code
- Adding features

**Debug manually when**:
- Build configuration errors
- Package version conflicts
- Metro cache issues
- Platform-specific problems (iOS vs Android)

**Why**: AI doesn't have real-time context about:
- Your installed package versions
- Your exact project structure
- Metro bundler state
- Platform-specific issues

---

## Debugging Checklist {#debugging-checklist}

### When Something Breaks

Follow this checklist **in order**:

#### 1. Clear Metro Cache
```bash
npm start -- --reset-cache
```

**Why**: Metro caches transformations. Config changes need fresh cache.

#### 2. Check File Existence

```bash
# Check all required files exist
ls babel.config.js
ls metro.config.js
ls tailwind.config.js
ls postcss.config.js
ls global.css
```

#### 3. Check Package Versions

```bash
npm list nativewind
npm list tailwindcss
npm list react-native-reanimated
```

**Expected** (as of Nov 2024):
- `nativewind@^4.2.1`
- `tailwindcss@^3.4.18`
- `react-native-reanimated@~3.10.0`

#### 4. Validate `tailwind.config.js` Content Array

```javascript
content: [
  './App.{js,jsx,ts,tsx}',
  './src/**/*.{js,jsx,ts,tsx}',
]
```

**Test**: Does this pattern match your file structure?

```bash
# Check what files exist
ls -R src/  # Should show your .tsx files

# If no src folder, update content:
content: [
  './App.{js,jsx,ts,tsx}',
  './screens/**/*.{js,jsx,ts,tsx}',  # or whatever you use
]
```

#### 5. Validate Babel Config Order

```javascript
presets: [
  ["babel-preset-expo", { jsxImportSource: "nativewind" }],  // ✅ First
  "nativewind/babel",  // ✅ Second
],
plugins: [
  "react-native-reanimated/plugin",  // ✅ LAST
]
```

#### 6. Check Metro Config Syntax

```javascript
// ✅ Correct
module.exports = withNativeWind(config, { input: './global.css' });

// ❌ Wrong
module.exports = config;  // Missing withNativeWind!
```

#### 7. Reinstall Dependencies

```bash
rm -rf node_modules
rm package-lock.json
npm install
```

#### 8. Check for TypeScript Errors

```bash
npx tsc --noEmit
```

If `className` not recognized:
- Check `nativewind-env.d.ts` exists
- Check it's in project root
- Restart TypeScript server in your IDE

#### 9. Test with Simple Component

Create `Test.tsx`:

```tsx
import { View, Text } from 'react-native';

export default function Test() {
  return (
    <View className="flex-1 bg-blue-500 items-center justify-center">
      <Text className="text-white text-2xl">
        If you see blue background, NativeWind works!
      </Text>
    </View>
  );
}
```

If this works but your app doesn't:
- Problem is in your app code, not configuration
- Check class names for typos
- Check custom colors defined in `tailwind.config.js`

#### 10. Check Logs for Specific Errors

```bash
npm start
```

Look for:
- `✅ NativeWind PostCSS` (good!)
- `❌ Cannot find module` (install missing package)
- `❌ Syntax error` (check config file syntax)

---

## Advanced Topics

### Custom Component Classes

**In `global.css`**:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer components {
  .btn {
    @apply px-4 py-2 rounded-lg font-semibold;
  }

  .btn-primary {
    @apply btn bg-blue-500 text-white;
  }

  .btn-secondary {
    @apply btn bg-gray-500 text-white;
  }

  .card {
    @apply bg-white rounded-xl shadow-lg p-4;
  }
}
```

**Usage**:

```tsx
<View className="card">
  <Text className="text-lg font-bold mb-2">Card Title</Text>
  <Text className="text-gray-600 mb-4">Card content</Text>
  <TouchableOpacity className="btn-primary">
    <Text>Action</Text>
  </TouchableOpacity>
</View>
```

**When to use**:
- Reusable components with consistent styling
- Complex combinations you use frequently
- Design system components

---

### Platform-Specific Styles

```tsx
import { Platform } from 'react-native';

<View
  className={`
    p-4 bg-white
    ${Platform.OS === 'ios' ? 'rounded-t-3xl' : 'rounded-t-lg'}
  `}
>
  <Text>Looks different on iOS vs Android</Text>
</View>
```

Or use NativeWind's platform modifiers:

```tsx
<View className="ios:pt-12 android:pt-8">
  <Text>Platform-specific padding</Text>
</View>
```

---

### Dark Mode Support

**1. Update `tailwind.config.js`**:

```javascript
module.exports = {
  darkMode: 'class',  // Enable dark mode
  content: ['./App.{js,jsx,ts,tsx}', './src/**/*.{js,jsx,ts,tsx}'],
  // ... rest of config
};
```

**2. Use dark variants**:

```tsx
<View className="bg-white dark:bg-black">
  <Text className="text-black dark:text-white">
    Adapts to theme
  </Text>
</View>
```

**3. Toggle theme** (with zustand):

```tsx
import { create } from 'zustand';
import { useColorScheme } from 'nativewind';

const useThemeStore = create((set) => ({
  theme: 'light',
  toggleTheme: () => set((state) => ({
    theme: state.theme === 'light' ? 'dark' : 'light'
  }))
}));

function App() {
  const { theme, toggleTheme } = useThemeStore();
  const { setColorScheme } = useColorScheme();

  useEffect(() => {
    setColorScheme(theme);
  }, [theme]);

  return (
    <View className="flex-1 bg-white dark:bg-black">
      <TouchableOpacity onPress={toggleTheme}>
        <Text>Toggle Theme</Text>
      </TouchableOpacity>
    </View>
  );
}
```

---

## Summary: The Key Takeaways

### For Humans

1. **Configuration is a pipeline** - Each file has a specific job
2. **Order matters** - Especially in Babel (Reanimated last!)
3. **Always clear cache** - After any config change
4. **Use specific versions** - NativeWind v4 syntax differs from v2
5. **Test incrementally** - Start simple, add complexity

### For Working with AI

1. **Be specific about versions** - "NativeWind v4" not just "NativeWind"
2. **Show your current state** - Paste config files when asking
3. **Mention what you've tried** - "I already cleared cache"
4. **Reference official docs** - Give AI the correct context
5. **Debug config manually** - AI struggles with build pipeline issues

### The Golden Rule

**When something breaks**:

```bash
# 1. Clear cache FIRST
npm start -- --reset-cache

# 2. Check file existence
ls babel.config.js metro.config.js tailwind.config.js

# 3. Check package versions
npm list nativewind tailwindcss

# 4. Reinstall if needed
rm -rf node_modules && npm install

# 5. Test with simple component
# Create Test.tsx with basic Tailwind classes
```

---

## Conclusion

You now understand:
- ✅ What each config file does
- ✅ How they work together as a pipeline
- ✅ Where to look when things break
- ✅ How to work effectively with AI coding tools

**Remember**: Configuration is about understanding **relationships between tools**. When AI gets stuck, it's usually because it lacks context about how Babel → Metro → PostCSS → Tailwind → NativeWind interact.

With this knowledge, you can:
1. Debug configuration issues yourself
2. Give AI better context when asking for help
3. Understand error messages
4. Customize your setup confidently

**Happy coding!** 🚀

---

## Additional Resources

- **NativeWind Official Docs**: https://www.nativewind.dev/
- **Tailwind CSS Docs**: https://tailwindcss.com/docs
- **Metro Bundler**: https://metrobundler.dev/
- **Expo Documentation**: https://docs.expo.dev/

---

*Written for developers building with AI tools*
*Last updated: November 2024*
*NativeWind v4 + Tailwind CSS v3 + Expo SDK 51*