"use client";

import { useEffect, useRef } from "react";

interface SCILScores {
  sensus: Record<string, number>;
  corpus: Record<string, number>;
  intellektus: Record<string, number>;
  lingua: Record<string, number>;
}

interface SCILPolygonProps {
  scores: SCILScores;
  size?: number;
  animated?: boolean;
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
  inner_presence: "Innere Präsenz",
  conviction: "Überzeugung",
  moment_focus: "Momentfokus",
  emotionality: "Emotionalität",
  appearance: "Erscheinung",
  gesture: "Gestik",
  facial_expression: "Mimik",
  spatial_presence: "Raumpräsenz",
  analytics: "Analytik",
  goal_orientation: "Zielorientierung",
  structure: "Struktur",
  objectivity: "Sachlichkeit",
  voice: "Stimme",
  articulation: "Artikulation",
  eloquence: "Eloquenz",
  imagery: "Bildhaftigkeit",
};

export function SCILPolygon({ scores, size = 400, animated = true }: SCILPolygonProps) {
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
    const maxRadius = size / 2 - 50;

    // Collect all frequencies in order
    const areas = ["sensus", "corpus", "intellektus", "lingua"] as const;
    const allFreqs: { area: string; key: string; value: number }[] = [];

    for (const area of areas) {
      const freqs = scores[area];
      for (const [key, value] of Object.entries(freqs)) {
        allFreqs.push({ area, key, value });
      }
    }

    const n = allFreqs.length;
    const angleStep = (2 * Math.PI) / n;

    // Clear with white background
    ctx.fillStyle = "#FFFFFF";
    ctx.fillRect(0, 0, size, size);

    // Draw grid rings
    for (let ring = 2; ring <= 10; ring += 2) {
      const r = (ring / 10) * maxRadius;
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, 2 * Math.PI);
      ctx.strokeStyle = ring === 10 ? "rgba(0,0,0,0.12)" : "rgba(0,0,0,0.05)";
      ctx.lineWidth = ring === 10 ? 1 : 0.5;
      ctx.stroke();

      // Ring label
      ctx.fillStyle = "rgba(0,0,0,0.2)";
      ctx.font = "9px sans-serif";
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
      ctx.strokeStyle = "rgba(0,0,0,0.06)";
      ctx.lineWidth = 0.5;
      ctx.stroke();
    }

    // Draw polygon (filled)
    ctx.beginPath();
    for (let i = 0; i < n; i++) {
      const angle = -Math.PI / 2 + i * angleStep;
      const r = (allFreqs[i].value / 10) * maxRadius;
      const x = cx + r * Math.cos(angle);
      const y = cy + r * Math.sin(angle);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.closePath();
    ctx.fillStyle = "rgba(11, 20, 55, 0.06)";
    ctx.fill();

    // Draw polygon outline with area colors
    let prevArea = "";
    for (let i = 0; i <= n; i++) {
      const idx = i % n;
      const angle = -Math.PI / 2 + idx * angleStep;
      const r = (allFreqs[idx].value / 10) * maxRadius;
      const x = cx + r * Math.cos(angle);
      const y = cy + r * Math.sin(angle);

      if (i > 0) {
        ctx.lineTo(x, y);
        ctx.strokeStyle = AREA_COLORS[allFreqs[idx].area];
        ctx.lineWidth = 2.5;
        ctx.stroke();
      }

      ctx.beginPath();
      ctx.moveTo(x, y);
      prevArea = allFreqs[idx].area;
    }

    // Draw dots and labels
    for (let i = 0; i < n; i++) {
      const angle = -Math.PI / 2 + i * angleStep;
      const r = (allFreqs[i].value / 10) * maxRadius;
      const x = cx + r * Math.cos(angle);
      const y = cy + r * Math.sin(angle);

      // Dot
      ctx.beginPath();
      ctx.arc(x, y, 4, 0, 2 * Math.PI);
      ctx.fillStyle = AREA_COLORS[allFreqs[i].area];
      ctx.fill();
      ctx.strokeStyle = "#fff";
      ctx.lineWidth = 1;
      ctx.stroke();

      // Label
      const labelR = maxRadius + 25;
      const lx = cx + labelR * Math.cos(angle);
      const ly = cy + labelR * Math.sin(angle);
      ctx.fillStyle = "rgba(0,0,0,0.5)";
      ctx.font = "10px sans-serif";
      ctx.textAlign = Math.cos(angle) > 0.1 ? "left" : Math.cos(angle) < -0.1 ? "right" : "center";
      ctx.textBaseline = Math.sin(angle) > 0.1 ? "top" : Math.sin(angle) < -0.1 ? "bottom" : "middle";
      ctx.fillText(FREQ_LABELS[allFreqs[i].key] || allFreqs[i].key, lx, ly);
    }

    // Area labels (in quadrants)
    const areaPositions = [
      { area: "sensus", angle: -Math.PI / 2 - Math.PI / 4 },
      { area: "corpus", angle: -Math.PI / 4 },
      { area: "intellektus", angle: Math.PI / 4 },
      { area: "lingua", angle: Math.PI / 2 + Math.PI / 4 },
    ];

    for (const { area, angle } of areaPositions) {
      const lr = maxRadius * 0.45;
      const lx = cx + lr * Math.cos(angle);
      const ly = cy + lr * Math.sin(angle);
      ctx.fillStyle = AREA_COLORS[area];
      ctx.font = "bold 12px sans-serif";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(AREA_LABELS[area], lx, ly);
    }
  }, [scores, size]);

  return (
    <div className="flex justify-center">
      <canvas ref={canvasRef} className={animated ? "polygon-animated" : ""} />
    </div>
  );
}
