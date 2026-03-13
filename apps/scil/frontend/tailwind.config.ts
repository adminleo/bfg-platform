import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // SCIL Branding (Orange/Gold)
        scil: {
          DEFAULT: "#E88D2A",
          dark: "#C67520",
          light: "#F5A84D",
        },
        // Dark Dashboard Theme
        surface: {
          DEFAULT: "#1E293B", // Slate 800
          dark: "#0F172A",    // Slate 900 — background
          hover: "#334155",   // Slate 700
          light: "#475569",   // Slate 600
        },
        border: {
          DEFAULT: "#334155", // Slate 700
        },
        // SCIL Frequency Colors
        freq: {
          sensus: "#E74C3C",
          corpus: "#F39C12",
          intellektus: "#3498DB",
          lingua: "#2ECC71",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [
    require("@tailwindcss/typography"),
  ],
};

export default config;
