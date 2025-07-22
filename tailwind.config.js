/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./frontend/**/*.{html,js}"],
  theme: {
    extend: {
      fontFamily: {
        'sans': ['Inter', 'system-ui', 'sans-serif'],
        'heading': ['Plus Jakarta Sans', 'system-ui', 'sans-serif'],
      },
      colors: {
        primary: {
          50: '#fff7ed',
          100: '#ffedd5',
          200: '#fed7aa',
          300: '#fdba74',
          400: '#fb923c',
          500: '#f97316', // Main burnt orange
          600: '#ea580c',
          700: '#c2410c',
          800: '#9a3412',
          900: '#7c2d12',
          950: '#431407',
        },
      }
    },
  },
  plugins: [],
}