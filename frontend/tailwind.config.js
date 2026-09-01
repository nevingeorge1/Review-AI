/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['"JetBrains Mono"', '"Fira Code"', 'Consolas', 'monospace'],
      },
      colors: {
        brand: {
          50: '#ecfeff',
          100: '#cffafe',
          200: '#a5f3fc',
          300: '#67e8f9',
          400: '#22d3ee',
          500: '#06b6d4',
          600: '#0891b2',
          700: '#0e7490',
          800: '#155e75',
          900: '#164e63',
          DEFAULT: '#06b6d4',
          accent: '#00f2fe',
        },
        slate: {
          850: '#131c2e',
          900: '#0f172a',
          950: '#080d1a',
        }
      },
      boxShadow: {
        'glow-brand': '0 0 35px -5px rgba(6, 182, 212, 0.35)',
        'glow-subtle': '0 0 20px -2px rgba(6, 182, 212, 0.15)',
        'premium': '0 20px 40px -15px rgba(0, 0, 0, 0.5), 0 0 1px 1px rgba(255, 255, 255, 0.08)',
        'card': '0 4px 20px -2px rgba(0, 0, 0, 0.3), 0 0 0 1px rgba(255, 255, 255, 0.06)',
        'card-hover': '0 8px 30px -4px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(6, 182, 212, 0.3)',
      },
      borderRadius: {
        '2xl': '16px',
        '3xl': '24px',
      },
      animation: {
        'fade-in': 'fadeIn 0.2s cubic-bezier(0.16, 1, 0.3, 1)',
        'slide-up': 'slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1)',
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(4px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(12px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
};
