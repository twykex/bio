/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./static/js/**/*.js"
  ],
  theme: {
    extend: {
      fontFamily: {
          sans: ['Plus Jakarta Sans', 'Inter', 'sans-serif'],
          mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      colors: {
        glass: {
          border: 'rgba(255, 255, 255, 0.08)',
          surface: 'rgba(255, 255, 255, 0.03)',
          highlight: 'rgba(255, 255, 255, 0.1)',
          input: 'rgba(0, 0, 0, 0.3)',
        },
        brand: {
            blue: '#3b82f6',
            purple: '#8b5cf6',
            cyan: '#06b6d4',
            emerald: '#10b981',
            rose: '#f43f5e',
            orange: '#f97316',
        },
        dark: {
            bg: '#050507',
            card: '#0e0e11',
            sidebar: '#08080a',
        },
        ios: {
            bg: '#000000',
            card: '#1C1C1E',
            border: '#2C2C2E',
            blue: '#0A84FF',
            orange: '#FF9F0A',
            text: '#F2F2F7',
            sub: '#8E8E93'
        }
      },
      animation: {
        'breathe': 'breathe 8s ease-in-out infinite',
        'scale-in': 'scaleIn 0.5s cubic-bezier(0.2, 0, 0.2, 1) forwards',
        'scan': 'scan 3s ease-in-out infinite',
        'float': 'float 6s ease-in-out infinite',
        'slide-up': 'slideUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards',
        'slide-down': 'slideDown 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards',
        'fade-in': 'fadeIn 1s ease-out forwards',
        'gradient-x': 'gradient-x 15s ease infinite',
        'blob': 'blob 7s infinite',
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'spin-slow': 'spin 3s linear infinite',
      },
      keyframes: {
        blob: {
          '0%': { transform: 'translate(0px, 0px) scale(1)' },
          '33%': { transform: 'translate(30px, -50px) scale(1.1)' },
          '66%': { transform: 'translate(-20px, 20px) scale(0.9)' },
          '100%': { transform: 'translate(0px, 0px) scale(1)' },
        },
        breathe: {
          '0%, 100%': { transform: 'scale(1)', opacity: '0.3' },
          '50%': { transform: 'scale(1.2)', opacity: '0.6' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.9)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        scan: {
          '0%': { top: '0%' },
          '50%': { top: '100%' },
          '100%': { top: '0%' },
        },
        float: {
            '0%, 100%': { transform: 'translateY(0)' },
            '50%': { transform: 'translateY(-10px)' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'gradient-x': {
          '0%, 100%': {
            'background-size': '200% 200%',
            'background-position': 'left center',
          },
          '50%': {
            'background-size': '200% 200%',
            'background-position': 'right center',
          },
        },
      }
    }
  },
  plugins: [],
}
