/** @type {import('tailwindcss').Config} */
module.exports = {
  mode: 'jit',
  content: [
      "./templates/**/*.html",
      "./static/src/**/*.js",
      "./node_modules/flowbite/**/*.js"
  ],
  theme: {
    colors: {
      'y-bg': '#FFF7B5',
      'y-text': '#808080',
    },
  },
  plugins: [
    require("flowbite/plugin")
  ],
}