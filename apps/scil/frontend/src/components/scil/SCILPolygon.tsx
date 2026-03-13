"use client";

import { useEffect, useRef } from "react";
import type { SCILScores } from "@/lib/types";

interface SCILPolygonProps {
  scores: SCILScores;
  size?: number;
}

const AREA_COLORS: Record<string, string> = {
  sensus: "#E74C3C",
  corpus: "#F39C12",
  intellektus: "#3498DB",
  lingua: "#2ECC71",
};

const AREA_LABELS: Record<string, string> = {
  sensus: "Sensus",
  corpus: "Corpus",
  intellektus: "Intellektus",
  lingua: "Lingua",
};

const FREQ_LABELS: Record<string, string> = {
  innere_praesenz: "Inn. Praesenz",
  innere_ueberzeugung: "Inn. Ueberzg.",
  prozessfokussierung: "Prozessfokus",
  emotionalitaet: "Emotionalitaet",
  erscheinungsbild: "Erscheinung",
  mimik: "Mimik",
  gestik: "Gestik",
  raeumliche_praesenz: "Raumpraesenz",
  sachlichkeit: "Sachlichkeit",
  analytik: "Analytik",
  struktur: "Struktur",
  zielorientierung: "Zielorient.",
  stimme: "Stimme",
  artikulation: "Artikulation",
  beredsamkeit: "Beredsamkeit",
  bildhaftigkeit: "Bildhaftigkeit",
};

export function SCILPolygon({ scores, size = 300 }: SCILPolygonProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const dpr = window.devicePixelRatio || 1;
    canvas.width = size * dpr;
    canvas.height = size * dpr;
    canvas.style.width = `${size}px`;
    canvas.style.height = `${size}px`;
    ctx.scale(dpr, dpr);

    const cx = size / 2;
    const cy = size / 2;
    const maxRadius = size / 2 - 40;

    // Collect all frequencies in order (4 areas x 4 frequencies)
    const areas = ["sensus", "corpus", "intellektus", "lingua"] as const;
    const allFreqs: { area: string; key: string; value: number }[] = [];

    for (const area of areas) {
      const freqs = scores[area] || {};
      for (const [key, value] of Object.entries(freqs)) {
        allFreqs.push({ area, key, value });
      }
    }

    const n = allFreqs.length;
    if (n === 0) return;
    const angleStep = (2 * Math.PI) / n;

    // Clear — transparent for dark theme
    ctx.clearRect(0, 0, size, size);

    // Draw grid rings (0-4 scale)
    for (let ring = 1; ring <= 4; ring++) {
      const r = (ring / 4) * maxRadius;
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, 2 * Math.PI);
      ctx.strokeStyle =
        ring === 4 ? "rgba(148,163,184,0.15)" : "rgba(148,163,184,0.08)";
      ctx.lineWidth = ring === 4 ? 1 : 0.5;
      ctx.stroke();

      // Ring label
      ctx.fillStyle = "rgba(148,163,184,0.3)";
      ctx.font = "9px system-ui";
      ctx.fillText(String(ring), cx + 3, cy - r + 10);
    }

    // Draw axis lines
    for (let i = 0; i < n; i++) {
      const angle = -Math.PI / 2 + i * angleStep;
      const x = cx + maxRadius * Math.cos(angle);
      const y = cy + maxRadius * Math.sin(angle);

      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.lineTo(x, y);
      ctx.strokeStyle = "rgba(148,163,184,0.06)";
      ctx.lineWidth = 0.5;
      ctx.stroke();
    }

    // Draw filled polygon
    ctx.beginPath();
    for (let i = 0; i < n; i++) {
      const angle = -Math.PI / 2 + i * angleStep;
      const r = (allFreqs[i].value / 4) * maxRadius;
      const x = cx + r * Math.cos(angle);
      const y = cy + r * Math.sin(angle);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.closePath();
    ctx.fillStyle = "rgba(232,141,42,0.08)";
    ctx.fill();

    // Draw polygon outline with area colors
    for (let i = 0; i < n; i++) {
      const idx0 = i;
      const idx1 = (i + 1) % n;
      const angle0 = -Math.PI / 2 + idx0 * angleStep;
      const angle1 = -Math.PI / 2 + idx1 * angleStep;
      const r0 = (allFreqs[idx0].value / 4) * maxRadius;
      const r1 = (allFreqs[idx1].value / 4) * maxRadius;
      const x0 = cx + r0 * Math.cos(angle0);
      const y0 = cy + r0 * Math.sin(angle0);
      const x1 = cx + r1 * Math.cos(angle1);
      const y1 = cy + r1 * Math.sin(angle1);

      ctx.beginPath();
      ctx.moveTo(x0, y0);
      ctx.lineTo(x1, y1);
      ctx.strokeStyle = AREA_COLORS[allFreqs[idx0].area];
      ctx.lineWidth = 2;
      ctx.stroke();
    }

    // Draw dots and labels
    for (let i = 0; i < n; i++) {
      const angle = -Math.PI / 2 + i * angleStep;
      const r = (allFreqs[i].value / 4) * maxRadius;
      const x = cx + r * Math.cos(angle);
      const y = cy + r * Math.sin(angle);

      // Dot
      ctx.beginPath();
      ctx.arc(x, y, 3, 0, 2 * Math.PI);
      ctx.fillStyle = AREA_COLORS[allFreqs[i].area];
      ctx.fill();
      ctx.strokeStyle = "#0F172A";
      ctx.lineWidth = 1;
      ctx.stroke();

      // Label
      const labelR = maxRadius + 20;
      const lx = cx + labelR * Math.cos(angle);
      const ly = cy + labelR * Math.sin(angle);
      ctx.fillStyle = "rgba(203,213,225,0.6)";
      ctx.font = "8px system-ui";
      ctx.textAlign =
        Math.cos(angle) > 0.1
          ? "left"
          : Math.cos(angle) < -0.1
          ? "right"
          : "center";
      ctx.textBaseline =
        Math.sin(angle) > 0.1
          ? "top"
          : Math.sin(angle) < -0.1
          ? "bottom"
          : "middle";
      ctx.fillText(FREQ_LABELS[allFreqs[i].key] || allFreqs[i].key, lx, ly);
    }

    // Area labels in quadrants
    const areaPositions = [
      { area: "sensus", angle: -Math.PI / 2 - Math.PI / 4 },
      { area: "corpus", angle: -Math.PI / 4 },
      { area: "intellektus", angle: Math.PI / 4 },
      { area: "lingua", angle: Math.PI / 2 + Math.PI / 4 },
    ];

    for (const { area, angle } of areaPositions) {
      const lr = maxRadius * 0.4;
      const lx = cx + lr * Math.cos(angle);
      const ly = cy + lr * Math.sin(angle);
      ctx.fillStyle = AREA_COLORS[area];
      ctx.font = "bold 10px system-ui";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(AREA_LABELS[area], lx, ly);
    }
  }, [scores, size]);

  return (
    <div className="flex justify-center polygon-animated">
      <canvas ref={canvasRef} />
    </div>
  );
}
