/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/*.html"],
  theme: {
    extend: {
      daisyui: {
        themes: ["dark"],
      },
    },
  },

  plugins: [require("daisyui")],
};
