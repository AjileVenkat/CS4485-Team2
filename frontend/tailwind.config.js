/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Space Grotesk"', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'ui-monospace', 'SFMono-Regular', 'monospace'],
      },
      boxShadow: {
        glow: '0 22px 48px -22px rgba(14, 116, 144, 0.6)',
      },
      keyframes: {
        liftIn: {
          '0%': {
            opacity: '0',
            transform: 'translateY(14px) scale(0.99)',
          },
          '100%': {
            opacity: '1',
            transform: 'translateY(0) scale(1)',
          },
        },
        pulseLine: {
          '0%, 100%': { opacity: '0.45' },
          '50%': { opacity: '1' },
        },
      },
      animation: {
        'lift-in': 'liftIn 650ms cubic-bezier(0.16, 1, 0.3, 1) both',
        'pulse-line': 'pulseLine 1.8s ease-in-out infinite',
      },
    },
  },
  plugins: [],
}

