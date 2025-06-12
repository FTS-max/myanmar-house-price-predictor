import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#0070f3',
          50: '#e6f0ff',
          100: '#cce0ff',
          200: '#99c2ff',
          300: '#66a3ff',
          400: '#3385ff',
          500: '#0070f3',
          600: '#0057c2',
          700: '#004299',
          800: '#002c66',
          900: '#001733',
        },
        secondary: {
          DEFAULT: '#7928ca',
          50: '#f3e8ff',
          100: '#e6d0ff',
          200: '#cda2ff',
          300: '#b573ff',
          400: '#9c45ff',
          500: '#7928ca',
          600: '#6020a1',
          700: '#481879',
          800: '#301050',
          900: '#180828',
        },
      },
      fontFamily: {
        sans: ['var(--font-geist-sans)'],
        mono: ['var(--font-geist-mono)'],
      },
    },
  },
  plugins: [],
};

export default config;