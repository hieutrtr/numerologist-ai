# Frontend Configuration Explained
## Babel, Metro, NativeWind, Tailwind, PostCSS

This document explains how all the build tools and styling systems work together in the mobile app.

---

## Overview: The Build Pipeline

```
Source Code (TypeScript/JSX)
    ↓
Babel Transform (JSX → JS, NativeWind)
    ↓
Metro Bundler (Bundle modules, CSS processing)
    ↓
PostCSS + Tailwind (Generate utility classes)
    ↓
React Native App (Running on device)
```

---

## 1. Babel Configuration (`babel.config.js`)

### Purpose
Babel transforms your modern JavaScript/TypeScript/JSX code into code that React Native can understand.

### Configuration Breakdown

```javascript
module.exports = function (api) {
  api.cache(true);  // Cache compilation results for faster builds

  return {
    presets: [
      // Core React Native + Expo preset
      ["babel-preset-expo", { jsxImportSource: "nativewind" }],

      // NativeWind preset (Tailwind for React Native)
      "nativewind/babel",
    ],

    plugins: [
      // Reanimated plugin MUST be last
      "react-native-reanimated/plugin",
    ],
  };
};
```

### What Each Part Does

#### 1. `babel-preset-expo`
```javascript
["babel-preset-expo", { jsxImportSource: "nativewind" }]
```
- **Default Expo transforms**: TypeScript, JSX, modern JS features
- **jsxImportSource: "nativewind"**: Changes how JSX is compiled to support NativeWind's styling

**Without this:**
```jsx
<View style={styles.container} />  // Traditional StyleSheet
```

**With this:**
```jsx
<View className="bg-primary p-4" />  // Tailwind classes work!
```

#### 2. `nativewind/babel`
- Processes Tailwind className props
- Converts `className="text-primary"` → actual style objects
- Integrates with Tailwind config

#### 3. `react-native-reanimated/plugin`
```javascript
"react-native-reanimated/plugin"  // MUST BE LAST!
```
- Enables Reanimated v3 worklets (smooth 60fps animations)
- Transforms animation code to run on UI thread
- **Critical**: Must be last plugin or animations break

---

## 2. Metro Configuration (`metro.config.js`)

### Purpose
Metro is React Native's JavaScript bundler (like Webpack for React Native). It bundles all your code and assets into a format the app can run.

### Configuration Breakdown

```javascript
const { getDefaultConfig } = require('expo/metro-config');
const { withNativeWind } = require('nativewind/metro');

const config = getDefaultConfig(__dirname);

// Enable NativeWind v4 CSS processing
module.exports = withNativeWind(config, { input: './global.css' });
```

### What This Does

#### 1. `getDefaultConfig(__dirname)`
Gets Expo's default Metro configuration:
- File extensions to bundle (`.js`, `.jsx`, `.ts`, `.tsx`)
- Asset types (images, fonts)
- Transform rules

#### 2. `withNativeWind(config, { input: './global.css' })`
Wraps Metro config to:
- **Process CSS file**: Reads `global.css`
- **Run Tailwind**: Generates utility classes
- **Inject styles**: Makes Tailwind classes available in app

**The Flow:**
```
global.css
  ↓
Metro reads file
  ↓
PostCSS processes (via Tailwind)
  ↓
Generates style mappings
  ↓
Available as className props in React Native
```

---

## 3. Tailwind Configuration (`tailwind.config.js`)

### Purpose
Defines all your design tokens, colors, spacing, fonts - the "design system" for your app.

### Configuration Breakdown

```javascript
module.exports = {
  // Files to scan for Tailwind classes
  content: [
    './App.{js,jsx,ts,tsx}',
    './src/**/*.{js,jsx,ts,tsx}',
    './app/**/*.{js,jsx,ts,tsx}',
  ],

  // NativeWind preset (React Native compatibility)
  presets: [require('nativewind/preset')],

  // Your custom design system
  theme: {
    extend: {
      colors: { /* ... */ },
      spacing: { /* ... */ },
      fontSize: { /* ... */ },
    },
  },
};
```

### Key Sections

#### 1. `content` Array
```javascript
content: [
  './App.{js,jsx,ts,tsx}',
  './src/**/*.{js,jsx,ts,tsx}',
]
```
**Purpose**: Tells Tailwind which files to scan for class names.

**Example**: If you use `className="bg-primary"` in `src/screens/Home.tsx`, Tailwind will:
1. Scan that file
2. Find `bg-primary`
3. Generate the CSS for that class
4. Include it in the final build

**Why this matters**: Unused classes are **not** included → smaller bundle size!

#### 2. `presets`
```javascript
presets: [require('nativewind/preset')]
```
**Purpose**: Loads NativeWind's preset configuration.

**What it does**:
- Adapts Tailwind for React Native (no browser-specific features)
- Maps CSS properties to React Native StyleSheet properties
- Handles platform differences (iOS vs Android)

**Example mappings**:
```
CSS                    → React Native
background-color       → backgroundColor
padding-left           → paddingLeft
flex-direction         → flexDirection
```

#### 3. `theme.extend`
Your custom design tokens:

```javascript
colors: {
  primary: {
    DEFAULT: '#d4af37',  // Gold
    dark: '#a8960b',
    light: '#f0d98f',
  },
  // Usage: bg-primary, bg-primary-dark, bg-primary-light
}
```

**Usage in code**:
```jsx
<View className="bg-primary p-md">
  <Text className="text-text-primary text-h1">
    Welcome
  </Text>
</View>
```

**Generated styles**:
```javascript
{
  backgroundColor: '#d4af37',
  padding: 16,  // from spacing.md
  color: '#ffffff',  // from text.primary
  fontSize: 24,  // from fontSize.h1
  lineHeight: 32,
  fontWeight: '700',
}
```

---

## 4. PostCSS Configuration (`postcss.config.js`)

### Purpose
PostCSS processes CSS files with plugins. Think of it as Babel but for CSS.

### Configuration Breakdown

```javascript
module.exports = {
  plugins: {
    tailwindcss: {},      // Process Tailwind directives
    autoprefixer: {},     // Add vendor prefixes (not used much in RN)
  },
};
```

### What Each Plugin Does

#### 1. `tailwindcss`
Processes Tailwind directives in `global.css`:

```css
/* Input: global.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Output: Generated CSS with all utility classes */
.bg-primary { background-color: #d4af37; }
.p-md { padding: 16px; }
.text-h1 { font-size: 24px; line-height: 32px; font-weight: 700; }
/* ... thousands more classes based on your config */
```

#### 2. `autoprefixer`
Adds vendor prefixes for browser compatibility:
```css
/* Not really needed for React Native, but included for web compatibility */
display: -webkit-box;
display: -webkit-flex;
display: flex;
```

---

## 5. Global CSS (`global.css`)

### Purpose
The entry point for Tailwind's CSS generation.

### Content

```css
@tailwind base;       /* Reset styles, base elements */
@tailwind components; /* Component classes (if you define any) */
@tailwind utilities;  /* All utility classes (bg-, text-, p-, etc.) */
```

### How It Works

1. **Metro reads this file** (configured in `metro.config.js`)
2. **PostCSS processes it** → Runs Tailwind plugin
3. **Tailwind generates classes** → Based on `tailwind.config.js`
4. **NativeWind injects styles** → Available as `className` props

---

## 6. NativeWind TypeScript Types (`nativewind-env.d.ts`)

### Purpose
TypeScript type definitions for NativeWind, enabling autocomplete and type checking.

### Content

```typescript
/// <reference types="nativewind/types" />
```

### What This Enables

**Without this:**
```tsx
<View className="bg-primary" />  // ❌ TypeScript error: className doesn't exist
```

**With this:**
```tsx
<View className="bg-primary p-4 flex-1" />  // ✅ Full autocomplete + type checking
```

**Autocomplete features**:
- All Tailwind classes
- Your custom colors (`bg-primary`)
- Your custom spacing (`p-md`)
- Your custom fonts (`text-h1`)

---

## How They All Work Together

### Example: Writing a Component

```tsx
// src/screens/Home.tsx
import { View, Text } from 'react-native';

export default function Home() {
  return (
    <View className="bg-dark flex-1 p-lg">
      <Text className="text-primary text-h1 mb-md">
        Welcome
      </Text>
      <Text className="text-text-secondary text-body">
        Let's begin your journey
      </Text>
    </View>
  );
}
```

### Build Process

#### Step 1: Babel Transform
```jsx
// Before Babel
<View className="bg-dark flex-1 p-lg">

// After Babel (simplified)
<View __nativewind_className="bg-dark flex-1 p-lg">
```

#### Step 2: Metro + NativeWind Processing
```javascript
// Metro reads global.css
// PostCSS + Tailwind generate classes
// NativeWind converts className to style prop

// Runtime result:
<View style={{
  backgroundColor: '#0d0d1a',  // from colors.dark
  flex: 1,
  padding: 24,  // from spacing.lg
}}>
```

#### Step 3: React Native Renders
```javascript
// Final native view
<NativeView style={[
  { backgroundColor: '#0d0d1a', flex: 1, padding: 24 }
]}>
```

---

## Configuration Flow Chart

```
┌─────────────────────────────────────────────────────────┐
│                    Source Code                          │
│  <View className="bg-primary p-md" />                   │
└────────────────────────┬────────────────────────────────┘
                         │
                         ↓
┌────────────────────────────────────────────────────────┐
│                 Babel Transform                         │
│  babel.config.js:                                       │
│  - babel-preset-expo (jsxImportSource: nativewind)     │
│  - nativewind/babel                                    │
│  - react-native-reanimated/plugin                      │
└────────────────────────┬───────────────────────────────┘
                         │
                         ↓
┌────────────────────────────────────────────────────────┐
│               Metro Bundler                             │
│  metro.config.js:                                       │
│  - withNativeWind(config, { input: './global.css' })  │
│  - Processes all source files                          │
│  - Bundles dependencies                                │
└────────────────────────┬───────────────────────────────┘
                         │
                         ↓
┌────────────────────────────────────────────────────────┐
│           PostCSS + Tailwind CSS                        │
│  postcss.config.js:                                     │
│  - tailwindcss plugin                                  │
│                                                         │
│  tailwind.config.js:                                   │
│  - Scans content files                                 │
│  - Generates utility classes                           │
│  - Uses custom theme (colors, spacing, etc.)           │
│                                                         │
│  global.css:                                           │
│  - @tailwind base/components/utilities                │
└────────────────────────┬───────────────────────────────┘
                         │
                         ↓
┌────────────────────────────────────────────────────────┐
│            NativeWind Runtime                           │
│  - Maps className → StyleSheet styles                  │
│  - Injects into React Native components               │
└────────────────────────┬───────────────────────────────┘
                         │
                         ↓
┌────────────────────────────────────────────────────────┐
│          React Native App Running                       │
│  <View style={{ backgroundColor: '#d4af37', ... }} /> │
└─────────────────────────────────────────────────────────┘
```

---

## Common Use Cases

### 1. Adding a New Color

**Step 1**: Update `tailwind.config.js`
```javascript
theme: {
  extend: {
    colors: {
      brand: {
        DEFAULT: '#FF6B6B',
        light: '#FFE5E5',
      }
    }
  }
}
```

**Step 2**: Use in code
```tsx
<View className="bg-brand" />
<Text className="text-brand-light" />
```

**Step 3**: Restart Metro
```bash
npm start -- --reset-cache
```

### 2. Adding Custom Spacing

**Step 1**: Update `tailwind.config.js`
```javascript
theme: {
  extend: {
    spacing: {
      'huge': '128px',
    }
  }
}
```

**Step 2**: Use in code
```tsx
<View className="p-huge" />  // padding: 128px
<View className="mt-huge" />  // marginTop: 128px
```

### 3. Creating Custom Font Sizes

**Step 1**: Update `tailwind.config.js`
```javascript
theme: {
  extend: {
    fontSize: {
      'mega': ['48px', { lineHeight: '56px', fontWeight: '900' }],
    }
  }
}
```

**Step 2**: Use in code
```tsx
<Text className="text-mega">Giant Text</Text>
```

---

## Debugging Tips

### Issue: Styles not applying

**Check 1**: Is the file in `content` array?
```javascript
// tailwind.config.js
content: [
  './src/**/*.{js,jsx,ts,tsx}',  // ✅ Should match your file path
]
```

**Check 2**: Clear Metro cache
```bash
npm start -- --reset-cache
```

**Check 3**: Check console for NativeWind errors

### Issue: TypeScript errors with className

**Solution**: Ensure `nativewind-env.d.ts` exists and is committed
```typescript
/// <reference types="nativewind/types" />
```

### Issue: Animations not working

**Check**: Reanimated plugin is **last** in Babel config
```javascript
plugins: [
  "react-native-reanimated/plugin",  // MUST BE LAST
]
```

---

## Performance Considerations

### 1. Tree Shaking (Automatic)
- Only classes you use are included
- Unused Tailwind classes = not bundled
- Keep `content` array accurate

### 2. Build Cache
- Metro caches transformations
- Faster subsequent builds
- Clear when changing config: `npm start -- --reset-cache`

### 3. Hot Reload
- Changes to components = hot reload (fast)
- Changes to config files = full reload (slow)

---

## Summary: Key Takeaways

1. **Babel**: Transforms your code (JSX → JS, enables NativeWind)
2. **Metro**: Bundles everything, processes CSS
3. **Tailwind**: Defines design system (colors, spacing, fonts)
4. **PostCSS**: Processes CSS (runs Tailwind)
5. **NativeWind**: Bridges Tailwind CSS → React Native styles
6. **global.css**: Entry point for Tailwind generation

**The Magic**: You write `className="bg-primary p-4"`, and the toolchain converts it to native styles that React Native understands!

---

*Last Updated: November 2024*
*Your Current Stack: Expo + NativeWind v4 + Tailwind v3*