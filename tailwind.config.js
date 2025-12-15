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
      },
      colors: {
        glass: {
          border: 'rgba(255, 255, 255, 0.08)',
          surface: 'rgba(255, 255, 255, 0.03)',
          highlight: 'rgba(255, 255, 255, 0.1)'
        },
        brand: {
            blue: '#3b82f6',
            purple: '#8b5cf6',
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
      },
      keyframes: {
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
      }
    }
  },
  plugins: [],
}
