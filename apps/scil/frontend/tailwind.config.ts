import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // SCIL Branding (Orange gradient)
        scil: {
          DEFAULT: "#E88D2A",
          dark: "#C67520",
          light: "#F5A84D",
          50: "#FFF7ED",
          100: "#FFEDD5",
        },
        // Light Dashboard Theme
        surface: {
          DEFAULT: "#FFFFFF",        // White cards
          dark: "#F5F5F7",           // Greyish-white background
          hover: "#F0F0F2",          // Hover state
          light: "#E8E8EC",          // Pressed / active
        },
        border: {
          DEFAULT: "rgba(0, 0, 0, 0.08)",
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
      backdropBlur: {
        xs: "2px",
      },
      boxShadow: {
        glass: "0 2px 20px rgba(0, 0, 0, 0.06)",
        "glass-sm": "0 1px 10px rgba(0, 0, 0, 0.04)",
        "glass-lg": "0 4px 30px rgba(0, 0, 0, 0.08)",
        card: "0 1px 3px rgba(0, 0, 0, 0.05), 0 1px 2px rgba(0, 0, 0, 0.03)",
        "card-hover": "0 4px 12px rgba(0, 0, 0, 0.08), 0 1px 3px rgba(0, 0, 0, 0.04)",
        glow: "0 0 20px rgba(232, 141, 42, 0.12)",
        "glow-sm": "0 0 10px rgba(232, 141, 42, 0.08)",
        "inner-glow": "inset 0 1px 0 0 rgba(255, 255, 255, 0.8)",
      },
      animation: {
        "fade-in": "fadeIn 0.3s ease-out",
        "fade-in-up": "fadeInUp 0.4s ease-out",
        "fade-in-down": "fadeInDown 0.3s ease-out",
        "scale-in": "scaleIn 0.2s ease-out",
        "slide-in-left": "slideInLeft 0.3s ease-out",
        "slide-in-right": "slideInRight 0.3s ease-out",
        shimmer: "shimmer 2s infinite linear",
        pulse_subtle: "pulseSubtle 3s infinite ease-in-out",
        float: "float 6s infinite ease-in-out",
      },
      keyframes: {
        fadeIn: {
          from: { opacity: "0" },
          to: { opacity: "1" },
        },
        fadeInUp: {
          from: { opacity: "0", transform: "translateY(12px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
        fadeInDown: {
          from: { opacity: "0", transform: "translateY(-8px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
        scaleIn: {
          from: { opacity: "0", transform: "scale(0.95)" },
          to: { opacity: "1", transform: "scale(1)" },
        },
        slideInLeft: {
          from: { opacity: "0", transform: "translateX(-16px)" },
          to: { opacity: "1", transform: "translateX(0)" },
        },
        slideInRight: {
          from: { opacity: "0", transform: "translateX(16px)" },
          to: { opacity: "1", transform: "translateX(0)" },
        },
        shimmer: {
          from: { backgroundPosition: "-200% 0" },
          to: { backgroundPosition: "200% 0" },
        },
        pulseSubtle: {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.7" },
        },
        float: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-6px)" },
        },
      },
    },
  },
  plugins: [
    require("@tailwindcss/typography"),
  ],
};

export default config;
