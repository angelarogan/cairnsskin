/** @type {import('tailwindcss').Config} */
export default {
  content: ["./src/**/*.{astro,html,js,jsx,md,mdx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          DEFAULT: "#0E0F0D",   // black
          soft: "#1C1D1B",      // soft black
        },
        paper: {
          DEFAULT: "#FFFFFF",   // white
          warm: "#FAF8F4",      // warm white
        },
        stone: {
          50: "#F7F6F3",
          100: "#EFEDE7",
          200: "#E3E0D8",
          300: "#CFCBC0",       // light grey / stone grey
          400: "#A9A59B",
          500: "#7D7A70",
          600: "#5B594F",
          700: "#3F3E37",
          800: "#2A2A25",
          900: "#1C1D1B",       // charcoal
        },
        eucalyptus: {
          50: "#F2F5F3",
          100: "#E2E8E3",
          200: "#C9D3CB",
          300: "#AFBEB4",
          400: "#9EADA3",       // accent
          500: "#87998D",
          600: "#6D8072",
          700: "#57665B",
        },
      },
      fontFamily: {
        sans: [
          "InterVariable",
          "Inter",
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "sans-serif",
        ],
        serif: [
          "\"Source Serif 4\"",
          "\"Iowan Old Style\"",
          "Georgia",
          "serif",
        ],
      },
      maxWidth: {
        prose: "68ch",
        editorial: "72rem",
      },
      backdropBlur: {
        xs: "4px",
      },
      boxShadow: {
        glass: "0 1px 1px rgba(14,15,13,0.03), 0 8px 24px rgba(14,15,13,0.05)",
        card: "0 1px 2px rgba(14,15,13,0.04), 0 2px 8px rgba(14,15,13,0.04)",
      },
      borderRadius: {
        xl2: "1.25rem",
      },
      transitionTimingFunction: {
        editorial: "cubic-bezier(0.4, 0, 0.2, 1)",
      },
    },
  },
  plugins: [],
};
