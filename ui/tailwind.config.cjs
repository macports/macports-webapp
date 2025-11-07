/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    "./app/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eef6ff",
          100: "#d9ebff",
          200: "#b3d7ff",
          300: "#85bfff",
          400: "#57a3ff",
          500: "#2e84ff",
          600: "#1d66db",
          700: "#154db0",
          800: "#123f8c",
          900: "#112f66"
        }
      }
    }
  },
  plugins: []
};
