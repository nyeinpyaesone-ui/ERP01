/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#172033",
        brand: "#3157d5",
        canvas: "#f5f7fb",
      },
    },
  },
  plugins: [],
};
