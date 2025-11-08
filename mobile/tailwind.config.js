/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './App.{js,jsx,ts,tsx}',
    './src/**/*.{js,jsx,ts,tsx}',
    './app/**/*.{js,jsx,ts,tsx}',
  ],
  presets: [require('nativewind/preset')],
  theme: {
    extend: {
      colors: {
        // Primary palette
        primary: {
          DEFAULT: '#d4af37', // Gold
          dark: '#a8960b',
          light: '#f0d98f',
        },
        secondary: {
          DEFAULT: '#8b5cf6', // Purple
          light: '#a78bfa',
          dark: '#7c3aed',
        },
        accent: '#5eead4', // Teal

        // Semantic colors
        success: '#5eead4',
        warning: '#fbbf24',
        error: '#ef4444',
        info: '#60a5fa',

        // Backgrounds
        dark: '#0d0d1a',
        light: '#1a1a33',
        card: '#1a1235',
        elevated: '#2d1b69',

        // Chat bubble backgrounds (lighter, more inviting)
        chat: {
          user: '#7C4DFF', // Vibrant purple for user messages
          userLight: '#9575CD', // Lighter purple variant
          assistant: '#FFCA28', // Warm gold for assistant messages
          assistantLight: '#FFD54F', // Lighter gold variant
        },

        // Text colors
        text: {
          primary: '#ffffff', // Pure white for better contrast
          secondary: '#FFD54F', // Bright warm gold
          muted: '#9E9E9E', // Lighter gray for better visibility
          inverse: '#0d0d1a',
          onPurple: '#ffffff', // White text on purple background
          onGold: '#1a1a33', // Dark text on gold background
        },

        // Borders
        border: {
          DEFAULT: '#333',
          focus: '#8b5cf6',
          error: '#ef4444',
        },
      },
      spacing: {
        xs: '4px',
        sm: '8px',
        md: '16px',
        lg: '24px',
        xl: '32px',
        xxl: '48px',
        xxxl: '64px',
      },
      fontSize: {
        display: ['32px', { lineHeight: '38px', fontWeight: '700' }],
        h1: ['24px', { lineHeight: '32px', fontWeight: '700' }],
        h2: ['18px', { lineHeight: '24px', fontWeight: '600' }],
        body: ['16px', { lineHeight: '24px', fontWeight: '400' }],
        small: ['14px', { lineHeight: '20px', fontWeight: '400' }],
        tiny: ['12px', { lineHeight: '16px', fontWeight: '400' }],
      },
      boxShadow: {
        'gold': '0 10px 20px rgba(212, 175, 55, 0.3)',
        'gold-lg': '0 15px 30px rgba(212, 175, 55, 0.4)',
        'purple': '0 10px 20px rgba(139, 92, 246, 0.3)',
      },
    },
  },
  plugins: [],
};
