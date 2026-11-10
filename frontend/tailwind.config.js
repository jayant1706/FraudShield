/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          950: '#070B19',
          900: '#0B132B',
          800: '#111D4A',
          700: '#1C2541',
          600: '#2A3656',
          500: '#3A506B',
        },
        fraud: {
          DEFAULT: '#EF4444',
          dark: '#B91C1C',
          light: '#FEE2E2',
        },
        legit: {
          DEFAULT: '#10B981',
          dark: '#047857',
          light: '#D1FAE5',
        },
        warning: {
          DEFAULT: '#F59E0B',
          dark: '#B45309',
          light: '#FEF3C7',
        }
      }
    },
  },
  plugins: [],
}

