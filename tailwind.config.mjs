/** @type {import('tailwindcss').Config} */
export default {
  content: ["./src/**/*.{astro,html,js,jsx,md,mdx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          DEFAULT: "#0D0E0C",   // black
          soft: "#1A1B18",      // soft black
        },
        paper: {
          DEFAULT: "#FFFFFF",   // white
          warm: "#FBF9F5",      // warm white
        },
        stone: {
          50: "#F7F5EF",
          100: "#F1EFE6",
          200: "#E5E1D4",
          300: "#D2CDBC",       // light grey / stone grey
          400: "#A9A48F",
          500: "#8C876F",
          600: "#716C5B",
          700: "#544F41",
          800: "#3A362C",
          900: "#2B2A24",       // charcoal
        },
        eucalyptus: {
          50: "#E7ECE6",        // eucalyptus-pale
          100: "#D8E1D5",
          200: "#C1CFBD",
          300: "#AABDA4",
          400: "#93A79A",       // accent (eucalyptus)
          500: "#7C9186",
          600: "#697F6E",
          700: "#57695D",       // eucalyptus-deep
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
        display: [
          "Fraunces",
          "\"Iowan Old Style\"",
          "Georgia",
          "serif",
        ],
        mono: [
          "\"JetBrains Mono\"",
          "ui-monospace",
          "SFMono-Regular",
          "monospace",
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
        glass: "inset 0 1px 0 rgba(255,255,255,0.6), 0 8px 24px -18px rgba(87,105,93,0.35)",
        "glass-hover": "inset 0 1px 0 rgba(255,255,255,0.6), 0 28px 54px -20px rgba(87,105,93,0.32)",
        "glass-dark": "inset 0 1px 0 rgba(255,255,255,0.08), 0 20px 40px -20px rgba(0,0,0,0.5)",
        nav: "inset 0 1px 0 rgba(255,255,255,0.6), 0 8px 32px -16px rgba(87,105,93,0.18)",
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
