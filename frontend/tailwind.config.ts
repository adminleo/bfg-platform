import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        // Gr8hub brand colors
        gr8: {
          navy: "#0B1437",          // Dark blue (primary)
          "navy-light": "#1B2559",  // Lighter navy
          neon: "#00E676",          // Neon green (accent)
          "neon-dark": "#00C853",   // Darker neon
          purple: "#7C3AED",        // Purple (secondary)
          "purple-light": "#A78BFA",// Lighter purple
          "purple-dark": "#5B21B6", // Darker purple
        },
        // SCIL frequency colors (keep for polygon)
        scil: {
          sensus: "#E74C3C",
          corpus: "#F39C12",
          intellektus: "#3498DB",
          lingua: "#2ECC71",
        },
      },
    },
  },
  plugins: [],
};

export default config;
