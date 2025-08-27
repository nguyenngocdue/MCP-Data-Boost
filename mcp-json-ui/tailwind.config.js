/** @type {import('tailwindcss').Config} */
export default {
content: ['./public/index.html', './src/**/*.{ts,tsx,js,jsx}'],
  theme: {
    extend: {},
  },
  plugins: [require("tailwindcss-animate"),],
}
  