/** @type {import('tailwindcss').Config} */
module.exports = {
  // CRITICAL: Point Tailwind to scan your JSX files for utility classes
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
