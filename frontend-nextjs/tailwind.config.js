/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'SFMono-Regular', 'monospace'],
      },
      colors: {
        brand: {
          50: '#f8f9fa',
          100: '#e9ecef',
          500: '#000000',
          600: '#1a1a1a',
        },
        sidebar: {
          bg: '#f5f5f5',
        },
        content: {
          bg: '#ffffff',
        },
        border: '#e5e5e5',
      },
    },
  },
  plugins: [],
}