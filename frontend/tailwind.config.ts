import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./hooks/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        gold: {
          DEFAULT: "#B89B5E",
          50: "#FBF6EA",
          100: "#F4E9C9",
          200: "#E7D293",
          300: "#D9BB5D",
          400: "#C4A547",
          500: "#B89B5E",
          600: "#8F783F",
          700: "#6B5A30",
          800: "#473C20",
          900: "#241E10",
        },
        rise: "#16A34A",
        fall: "#DC2626",
        hoverbg: "rgba(254, 252, 232, 1)",
      },
      fontFamily: {
        sans: ["var(--font-app)", "system-ui", "sans-serif"],
        brand: ["var(--font-brand)", "Cinzel", "Trajan Pro", "serif"],
      },
      boxShadow: {
        card: "0 4px 12px rgba(184, 155, 94, 0.15)",
      },
      transitionTimingFunction: {
        soft: "cubic-bezier(0.4, 0, 0.2, 1)",
      },
    },
  },
  plugins: [],
};

export default config;
