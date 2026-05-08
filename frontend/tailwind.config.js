/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        tiktok: {
          pink: '#FE2C55',
          blue: '#25F4EE',
          dark: '#121212',
          darker: '#0a0a0a',
          card: '#1e1e1e',
          gray: '#2f2f2f',
        },
      },
    },
  },
  plugins: [],
}
