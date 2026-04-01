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
  innere_praesenz: "Inn. Praes.",
  innere_ueberzeugung: "Inn. Uebzg.",
  prozessfokussierung: "Prozessfok.",
  emotionalitaet: "Emotional.",
  erscheinungsbild: "Erschein.",
  mimik: "Mimik",
  gestik: "Gestik",
  raeumliche_praesenz: "Raumpr.",
  sachlichkeit: "Sachlichk.",
  analytik: "Analytik",
  struktur: "Struktur",
  zielorientierung: "Zielorient.",
  stimme: "Stimme",
  artikulation: "Artikulat.",
  beredsamkeit: "Beredsam.",
  bildhaftigkeit: "Bildhaft.",
};

export function SCILPolygon({ scores, size = 280 }: SCILPolygonProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const dpr = window.devicePixelRatio || 1;
    // Canvas = exactly the size prop, polygon shrunk to leave room for labels
    canvas.width = size * dpr;
    canvas.height = size * dpr;
    canvas.style.width = `${size}px`;
    canvas.style.height = `${size}px`;
    ctx.scale(dpr, dpr);

    const cx = size / 2;
    const cy = size / 2;
    // Shrink polygon radius to leave generous room for labels inside canvas
    const maxRadius = size / 2 - 55;

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

    // Clear
    ctx.clearRect(0, 0, size, size);

    // Draw grid rings (0-4 scale)
    for (let ring = 1; ring <= 4; ring++) {
      const r = (ring / 4) * maxRadius;
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, 2 * Math.PI);
      ctx.strokeStyle =
        ring === 4 ? "rgba(100,116,139,0.18)" : "rgba(100,116,139,0.08)";
      ctx.lineWidth = ring === 4 ? 1 : 0.5;
      ctx.stroke();

      // Ring label
      ctx.fillStyle = "rgba(100,116,139,0.35)";
      ctx.font = "9px system-ui";
      ctx.textAlign = "left";
      ctx.textBaseline = "bottom";
      ctx.fillText(String(ring), cx + 3, cy - r - 1);
    }

    // Draw axis lines
    for (let i = 0; i < n; i++) {
      const angle = -Math.PI / 2 + i * angleStep;
      const x = cx + maxRadius * Math.cos(angle);
      const y = cy + maxRadius * Math.sin(angle);

      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.lineTo(x, y);
      ctx.strokeStyle = "rgba(100,116,139,0.07)";
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
    ctx.fillStyle = "rgba(232,141,42,0.07)";
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
      ctx.arc(x, y, 3.5, 0, 2 * Math.PI);
      ctx.fillStyle = AREA_COLORS[allFreqs[i].area];
      ctx.fill();
      ctx.strokeStyle = "#FFFFFF";
      ctx.lineWidth = 1.5;
      ctx.stroke();

      // Label + score — placed just outside the outer ring
      const labelR = maxRadius + 12;
      const lx = cx + labelR * Math.cos(angle);
      const ly = cy + labelR * Math.sin(angle);

      const label = FREQ_LABELS[allFreqs[i].key] || allFreqs[i].key;
      const scoreVal = allFreqs[i].value.toFixed(1);

      // Text alignment based on position
      const cosA = Math.cos(angle);
      const sinA = Math.sin(angle);
      ctx.textAlign =
        cosA > 0.15 ? "left" : cosA < -0.15 ? "right" : "center";
      ctx.textBaseline =
        sinA > 0.15 ? "top" : sinA < -0.15 ? "bottom" : "middle";

      // Label name
      ctx.fillStyle = "rgba(51,65,85,0.7)";
      ctx.font = "500 9px system-ui";
      ctx.fillText(label, lx, ly);

      // Score value (colored, below/above label)
      const scoreOffsetY = sinA > 0.15 ? 11 : sinA < -0.15 ? -11 : 10;
      ctx.fillStyle = AREA_COLORS[allFreqs[i].area];
      ctx.font = "bold 9px system-ui";
      ctx.fillText(scoreVal, lx, ly + scoreOffsetY);
    }

    // Area labels in quadrants
    const areaPositions = [
      { area: "sensus", angle: -Math.PI / 2 - Math.PI / 4 },
      { area: "corpus", angle: -Math.PI / 4 },
      { area: "intellektus", angle: Math.PI / 4 },
      { area: "lingua", angle: Math.PI / 2 + Math.PI / 4 },
    ];

    for (const { area, angle } of areaPositions) {
      const lr = maxRadius * 0.38;
      const lx = cx + lr * Math.cos(angle);
      const ly = cy + lr * Math.sin(angle);
      ctx.fillStyle = AREA_COLORS[area];
      ctx.font = "bold 11px system-ui";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.globalAlpha = 0.8;
      ctx.fillText(AREA_LABELS[area], lx, ly);
      ctx.globalAlpha = 1.0;
    }
  }, [scores, size]);

  return (
    <div className="flex justify-center polygon-animated overflow-hidden">
      <canvas ref={canvasRef} style={{ maxWidth: "100%" }} />
    </div>
  );
}
