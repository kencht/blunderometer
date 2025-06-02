/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        chess: {
          light: '#f0d9b5',
          dark: '#b58863',
          blunder: '#dc2626',
          mistake: '#ea580c',
          inaccuracy: '#ca8a04',
          good: '#16a34a'
        }
      }
    },
  }
}
