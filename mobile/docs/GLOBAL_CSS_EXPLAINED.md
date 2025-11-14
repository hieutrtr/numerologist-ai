# Global CSS Explained
## Understanding `global.css` in React Native with NativeWind

This guide explains what `global.css` is, why it's needed, and how it works in a React Native app with NativeWind.

---

## What is `global.css`?

### The File

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

That's it! Just three lines. But these three directives are incredibly powerful.

### Purpose

`global.css` is the **entry point** for Tailwind CSS generation. It tells Tailwind:
1. Where to inject generated CSS
2. Which layers to generate (base, components, utilities)
3. How to organize the output

---

## The Three Directives Explained

### 1. `@tailwind base;`

**What it generates**: Reset styles and base element styles

**In a web browser, this would be**:
```css
/* Normalize/reset styles */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: system-ui, sans-serif;
  line-height: 1.5;
}

/* Base element styles */
h1, h2, h3, h4, h5, h6 {
  font-weight: bold;
}
```

**In React Native (via NativeWind)**:
- Not really used (React Native has no HTML elements)
- NativeWind mostly ignores this
- Safe to include for web compatibility if using Expo web

### 2. `@tailwind components;`

**What it generates**: Component classes you define

**Example - if you define custom components**:
```css
@layer components {
  .btn-primary {
    @apply bg-primary text-white px-4 py-2 rounded-lg;
  }
}
```

**This would generate**:
```css
.btn-primary {
  background-color: #007AFF;
  color: #FFFFFF;
  padding-left: 16px;
  padding-right: 16px;
  padding-top: 8px;
  padding-bottom: 8px;
  border-radius: 8px;
}
```

**In React Native**:
```tsx
<TouchableOpacity className="btn-primary">
  <Text>Click Me</Text>
</TouchableOpacity>
```

**Note**: Most React Native apps don't define custom component classes. You typically just use utility classes directly.

### 3. `@tailwind utilities;`

**What it generates**: ALL the utility classes (the main feature!)

**This is the big one**. It generates thousands of utility classes based on your `tailwind.config.js`:

```css
/* Colors */
.bg-primary { background-color: #007AFF; }
.bg-secondary { background-color: #5856D6; }
.text-primary { color: #000000; }
.text-white { color: #FFFFFF; }

/* Spacing */
.p-0 { padding: 0px; }
.p-1 { padding: 4px; }
.p-2 { padding: 8px; }
.p-4 { padding: 16px; }
.m-4 { margin: 16px; }
.px-4 { padding-left: 16px; padding-right: 16px; }
.py-2 { padding-top: 8px; padding-bottom: 8px; }

/* Layout */
.flex { display: flex; }
.flex-row { flex-direction: row; }
.flex-col { flex-direction: column; }
.items-center { align-items: center; }
.justify-between { justify-content: space-between; }

/* Typography */
.text-xs { font-size: 12px; line-height: 16px; }
.text-sm { font-size: 14px; line-height: 20px; }
.text-lg { font-size: 18px; line-height: 28px; }
.font-bold { font-weight: 700; }

/* Borders */
.rounded { border-radius: 4px; }
.rounded-lg { border-radius: 8px; }
.border { border-width: 1px; }

/* ... thousands more classes */
```

---

## How `global.css` is Processed

### The Complete Flow

```
1. You write code:
   <View className="bg-primary p-4" />

2. Metro reads global.css
   (configured in metro.config.js)

3. PostCSS processes global.css
   - Reads the @tailwind directives
   - Runs Tailwind CSS plugin

4. Tailwind CSS plugin:
   - Scans your source files (from content in tailwind.config.js)
   - Finds: "bg-primary" and "p-4"
   - Looks up in tailwind.config.js:
     * bg-primary → colors.primary.DEFAULT → #007AFF
     * p-4 → spacing[4] → 16px
   - Generates CSS for those classes

5. NativeWind receives generated CSS:
   {
     "bg-primary": { backgroundColor: "#007AFF" },
     "p-4": { padding: 16 }
   }

6. At runtime, NativeWind converts:
   className="bg-primary p-4"
   → style={{ backgroundColor: "#007AFF", padding: 16 }}

7. React Native renders:
   <NativeView style={{ backgroundColor: "#007AFF", padding: 16 }} />
```

### Visual Diagram

```
┌─────────────────────────────────────────────────┐
│  global.css                                     │
│                                                 │
│  @tailwind base;                               │
│  @tailwind components;                         │
│  @tailwind utilities;                          │
└────────────┬────────────────────────────────────┘
             │
             ↓
┌─────────────────────────────────────────────────┐
│  Metro Bundler                                  │
│  (configured via metro.config.js)              │
│                                                 │
│  withNativeWind(config, {                      │
│    input: './global.css'  ← Points to this file│
│  })                                            │
└────────────┬────────────────────────────────────┘
             │
             ↓
┌─────────────────────────────────────────────────┐
│  PostCSS                                        │
│  (configured via postcss.config.js)            │
│                                                 │
│  plugins: {                                    │
│    tailwindcss: {} ← Processes @tailwind       │
│  }                                             │
└────────────┬────────────────────────────────────┘
             │
             ↓
┌─────────────────────────────────────────────────┐
│  Tailwind CSS Plugin                           │
│                                                 │
│  1. Reads tailwind.config.js                   │
│  2. Scans content files for class names        │
│  3. Generates CSS for found classes            │
└────────────┬────────────────────────────────────┘
             │
             ↓
┌─────────────────────────────────────────────────┐
│  Generated CSS (in memory)                     │
│                                                 │
│  .bg-primary { background-color: #007AFF; }    │
│  .p-4 { padding: 16px; }                       │
│  .text-lg { font-size: 18px; }                 │
│  ... etc                                       │
└────────────┬────────────────────────────────────┘
             │
             ↓
┌─────────────────────────────────────────────────┐
│  NativeWind Runtime                            │
│                                                 │
│  Converts className → React Native style      │
│  Available in your components                  │
└─────────────────────────────────────────────────┘
```

---

## Why These Three Directives?

### Historical Context

Tailwind CSS was originally designed for web browsers. The three layers (`base`, `components`, `utilities`) provide organization:

1. **Base**: Foundation styles (resets, defaults)
2. **Components**: Reusable component classes
3. **Utilities**: Single-purpose utility classes

### In React Native

For React Native with NativeWind, you typically only care about **utilities**. But we include all three directives for:

1. **Consistency**: Standard Tailwind setup
2. **Web compatibility**: If using Expo web target
3. **Future-proofing**: If you want to add custom components later

---

## Common Questions

### Q: Can I delete `global.css`?

**A**: No! Metro needs this file to know where to inject Tailwind.

Without it:
```javascript
// metro.config.js
withNativeWind(config, { input: './global.css' })  // ← Must exist
```

### Q: Can I add custom CSS to `global.css`?

**A**: Yes! You can add custom styles:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Custom component classes */
@layer components {
  .btn-primary {
    @apply bg-primary text-white px-4 py-2 rounded-lg font-semibold;
  }

  .card {
    @apply bg-white p-4 rounded-xl shadow-lg;
  }
}

/* Custom utilities */
@layer utilities {
  .text-shadow {
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
  }
}
```

**Usage**:
```tsx
<View className="card">
  <TouchableOpacity className="btn-primary">
    <Text className="text-shadow">Click Me</Text>
  </TouchableOpacity>
</View>
```

### Q: Do I need to import `global.css` in my components?

**A**: No! Metro automatically processes it. Never import it:

```tsx
// ❌ DON'T DO THIS
import './global.css';

// ✅ Just use className
<View className="bg-primary" />
```

### Q: What if I want different styles per platform (iOS/Android)?

**A**: Use Tailwind's arbitrary values or React Native's Platform API:

```tsx
// Option 1: Tailwind arbitrary values (inline styles)
<View className="bg-primary p-4 ios:pt-8 android:pt-6" />

// Option 2: Platform API (more control)
import { Platform } from 'react-native';

<View className={`bg-primary p-4 ${Platform.OS === 'ios' ? 'pt-8' : 'pt-6'}`} />
```

### Q: How do I know what classes are available?

**A**: All classes are defined by your `tailwind.config.js`:

```javascript
// tailwind.config.js
theme: {
  extend: {
    colors: {
      primary: '#007AFF',      // → bg-primary, text-primary, border-primary
      secondary: '#5856D6',    // → bg-secondary, text-secondary, etc.
    },
    spacing: {
      xs: '4px',               // → p-xs, m-xs, gap-xs, etc.
      sm: '8px',               // → p-sm, m-sm, gap-sm, etc.
    }
  }
}
```

**Available patterns**:
- `bg-{color}` - Background colors
- `text-{color}` - Text colors
- `border-{color}` - Border colors
- `p-{size}` - Padding (all sides)
- `px-{size}` - Padding horizontal
- `py-{size}` - Padding vertical
- `m-{size}` - Margin (all sides)
- And hundreds more...

### Q: Can I use Tailwind directives in component files?

**A**: No, only in `.css` files. Use `className` in `.tsx` files:

```tsx
// ❌ DON'T DO THIS
const MyComponent = () => (
  <View>
    <style>
      @apply bg-primary;
    </style>
  </View>
);

// ✅ DO THIS
const MyComponent = () => (
  <View className="bg-primary" />
);
```

---

## Advanced Usage

### Creating Custom Component Classes

**In `global.css`**:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer components {
  /* Button variants */
  .btn {
    @apply px-4 py-2 rounded-lg font-semibold;
  }

  .btn-primary {
    @apply btn bg-primary text-white;
  }

  .btn-secondary {
    @apply btn bg-secondary text-white;
  }

  .btn-outline {
    @apply btn bg-transparent border-2 border-primary text-primary;
  }

  /* Card components */
  .card {
    @apply bg-white rounded-xl shadow-lg;
  }

  .card-header {
    @apply p-4 border-b border-gray-200;
  }

  .card-body {
    @apply p-4;
  }
}
```

**Usage**:
```tsx
<View className="card">
  <View className="card-header">
    <Text className="text-lg font-bold">Card Title</Text>
  </View>
  <View className="card-body">
    <Text>Card content here</Text>
    <TouchableOpacity className="btn-primary">
      <Text>Action</Text>
    </TouchableOpacity>
  </View>
</View>
```

### Adding Theme Variants

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Dark mode utilities */
@layer utilities {
  .dark .dark\:bg-dark {
    background-color: #000000;
  }

  .dark .dark\:text-white {
    color: #FFFFFF;
  }
}
```

**Usage**:
```tsx
<View className="bg-white dark:bg-dark">
  <Text className="text-black dark:text-white">
    Adapts to dark mode
  </Text>
</View>
```

---

## Debugging

### Issue: Changes to `global.css` not applying

**Solution**: Clear Metro cache
```bash
npm start -- --reset-cache
```

### Issue: Custom classes not working

**Check 1**: Are they in a `@layer` directive?
```css
/* ❌ Won't work */
.my-class {
  background-color: red;
}

/* ✅ Works */
@layer components {
  .my-class {
    @apply bg-red-500;
  }
}
```

**Check 2**: Clear cache and reload
```bash
npm start -- --reset-cache
```

### Issue: File not found error

**Check**: Metro config points to correct file
```javascript
// metro.config.js
module.exports = withNativeWind(config, {
  input: './global.css'  // ← Must match actual filename and location
});
```

---

## Performance Considerations

### Tree Shaking

Tailwind only includes classes you actually use:

```tsx
// You use these classes:
<View className="bg-primary p-4 flex-1" />
<Text className="text-lg font-bold" />

// Only these classes are bundled:
// bg-primary, p-4, flex-1, text-lg, font-bold

// These are NOT bundled (not used):
// bg-secondary, p-8, flex-2, text-xl, font-light, etc.
```

**Result**: Small bundle size even though Tailwind has thousands of classes.

### Build Time

**First build**: Slower (scans all files, generates CSS)
**Subsequent builds**: Fast (Metro caches results)

**To improve**:
1. Keep `content` array in `tailwind.config.js` focused
2. Don't scan unnecessary directories
3. Use Metro's cache (don't clear unless needed)

---

## Summary

### What `global.css` Does

1. **Declares layers**: `@tailwind base/components/utilities`
2. **Entry point**: Metro reads it to start CSS generation
3. **Injection point**: Where Tailwind injects generated classes
4. **Customization**: Where you add custom component classes

### The Magic

```
global.css (@tailwind directives)
    ↓
Metro processes (withNativeWind)
    ↓
PostCSS + Tailwind generate classes
    ↓
NativeWind makes available at runtime
    ↓
You use className props
    ↓
React Native renders with styles
```

### Key Takeaways

- ✅ **Required file** - Don't delete
- ✅ **Three directives** - base, components, utilities
- ✅ **Processed by Metro** - Never import directly
- ✅ **Customizable** - Add custom component classes
- ✅ **Tree-shaken** - Only used classes bundled

---

## Related Documentation

- **Build Pipeline**: See `FRONTEND_CONFIG_EXPLAINED.md` for complete build process
- **Tailwind Config**: See `tailwind.config.js` for available classes
- **Metro Config**: See `metro.config.js` for bundler setup

---

*Last Updated: November 2024*
*NativeWind v4 + Tailwind CSS v3*