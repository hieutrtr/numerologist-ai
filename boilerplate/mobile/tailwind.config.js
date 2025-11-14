/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './App.{js,jsx,ts,tsx}',
    './src/**/*.{js,jsx,ts,tsx}',
  ],
  presets: [require('nativewind/preset')],
  theme: {
    extend: {
      colors: {
        // Customize your color palette here
        primary: {
          DEFAULT: '#007AFF',
          dark: '#0051D5',
          light: '#5AC8FA',
        },
        secondary: {
          DEFAULT: '#5856D6',
          light: '#AF52DE',
          dark: '#32ADE6',
        },

        // Background colors
        background: {
          DEFAULT: '#FFFFFF',
          dark: '#000000',
          elevated: '#F2F2F7',
        },

        // Text colors
        text: {
          primary: '#000000',
          secondary: '#3C3C43',
          tertiary: '#8E8E93',
          inverse: '#FFFFFF',
        },

        // Semantic colors
        success: '#34C759',
        warning: '#FF9500',
        error: '#FF3B30',
        info: '#007AFF',
      },
      spacing: {
        xs: '4px',
        sm: '8px',
        md: '16px',
        lg: '24px',
        xl: '32px',
        '2xl': '48px',
        '3xl': '64px',
      },
      fontSize: {
        xs: ['12px', { lineHeight: '16px' }],
        sm: ['14px', { lineHeight: '20px' }],
        base: ['16px', { lineHeight: '24px' }],
        lg: ['18px', { lineHeight: '28px' }],
        xl: ['20px', { lineHeight: '28px' }],
        '2xl': ['24px', { lineHeight: '32px', fontWeight: '600' }],
        '3xl': ['30px', { lineHeight: '36px', fontWeight: '700' }],
        '4xl': ['36px', { lineHeight: '40px', fontWeight: '800' }],
      },
    },
  },
  plugins: [],
};
