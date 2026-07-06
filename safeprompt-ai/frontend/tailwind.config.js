/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    './index.html',
    './src/**/*.{js,jsx,ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        // Brand palette used throughout the dashboard and gauges.
        brand: {
          50: '#eef4ff',
          100: '#dbe6fe',
          200: '#bed0fd',
          300: '#91b0fb',
          400: '#5f87f7',
          500: '#3b63f0',
          600: '#2645e4',
          700: '#1f36c9',
          800: '#1f2fa2',
          900: '#1e2c81',
        },
        risk: {
          safe: '#22c55e',
          low: '#84cc16',
          medium: '#f59e0b',
          high: '#f97316',
          critical: '#ef4444',
        },
        surface: {
          light: '#f8fafc',
          dark: '#0f172a',
          darkCard: '#1e293b',
        },
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        card: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)',
      },
    },
  },
  plugins: [],
}
