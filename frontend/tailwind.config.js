/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        // Deep cool graphite — an editing-suite monitor, not pure black.
        base: {
          DEFAULT: "#14161C",
          panel: "#1C1F27",
          raised: "#242833",
          hairline: "#2E323E",
        },
        ink: {
          DEFAULT: "#EDEBE4",
          muted: "#9AA0AC",
          faint: "#5B606E",
        },
        // Tally light amber — the "recording" state, used sparingly as the signature accent.
        tally: {
          DEFAULT: "#F2A93B",
          dim: "#7A5B26",
        },
        // Scope teal — the "live/complete" trace color, used for active/success states.
        scope: {
          DEFAULT: "#4FD1C5",
          dim: "#2C6D66",
        },
        alert: "#E0645A",
      },
      fontFamily: {
        display: ["Sora", "sans-serif"],
        body: ["Inter", "sans-serif"],
        mono: ["'IBM Plex Mono'", "monospace"],
      },
      boxShadow: {
        panel: "0 1px 0 0 rgba(255,255,255,0.03) inset, 0 8px 24px -12px rgba(0,0,0,0.6)",
      },
      keyframes: {
        "fade-in": {
          "0%": { opacity: "0", transform: "translateY(4px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
      animation: {
        "fade-in": "fade-in 0.2s ease-out",
      },
    },
  },
  plugins: [],
};
