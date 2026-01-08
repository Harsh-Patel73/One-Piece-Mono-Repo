/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // One Piece themed colors
        'op-red': '#E53935',
        'op-blue': '#1E88E5',
        'op-green': '#43A047',
        'op-purple': '#8E24AA',
        'op-yellow': '#FDD835',
        'op-black': '#212121',
      },
      fontFamily: {
        'display': ['Bangers', 'cursive'],
      },
    },
  },
  plugins: [],
}
