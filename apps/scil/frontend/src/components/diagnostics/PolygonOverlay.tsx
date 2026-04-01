"use client";

import { useEffect, useRef } from "react";

interface SCILScores {
  sensus: Record<string, number>;
  corpus: Record<string, number>;
  intellektus: Record<string, number>;
  lingua: Record<string, number>;
}

interface PolygonOverlayProps {
  selfScores: SCILScores;
  othersScores: SCILScores;
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

export function PolygonOverlay({ selfScores, othersScores, size = 450 }: PolygonOverlayProps) {
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
    const maxRadius = size / 2 - 55;

    const areas = ["sensus", "corpus", "intellektus", "lingua"] as const;

    // Collect all frequencies from self scores
    const allFreqs: { area: string; key: string }[] = [];
    for (const area of areas) {
      for (const key of Object.keys(selfScores[area])) {
        allFreqs.push({ area, key });
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

    // Helper: draw a polygon
    const drawPolygon = (
      scores: SCILScores,
      fillColor: string,
      strokeColor: string,
      lineWidth: number,
      dashPattern: number[] = [],
    ) => {
      // Fill
      ctx.beginPath();
      for (let i = 0; i < n; i++) {
        const angle = -Math.PI / 2 + i * angleStep;
        const val = scores[allFreqs[i].area as keyof SCILScores]?.[allFreqs[i].key] ?? 0;
        const r = (val / 10) * maxRadius;
        const x = cx + r * Math.cos(angle);
        const y = cy + r * Math.sin(angle);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.closePath();
      ctx.fillStyle = fillColor;
      ctx.fill();

      // Stroke segments with area colors
      ctx.setLineDash(dashPattern);
      for (let i = 0; i < n; i++) {
        const i2 = (i + 1) % n;
        const angle1 = -Math.PI / 2 + i * angleStep;
        const angle2 = -Math.PI / 2 + i2 * angleStep;
        const val1 = scores[allFreqs[i].area as keyof SCILScores]?.[allFreqs[i].key] ?? 0;
        const val2 = scores[allFreqs[i2].area as keyof SCILScores]?.[allFreqs[i2].key] ?? 0;
        const r1 = (val1 / 10) * maxRadius;
        const r2 = (val2 / 10) * maxRadius;

        ctx.beginPath();
        ctx.moveTo(cx + r1 * Math.cos(angle1), cy + r1 * Math.sin(angle1));
        ctx.lineTo(cx + r2 * Math.cos(angle2), cy + r2 * Math.sin(angle2));
        ctx.strokeStyle = strokeColor === "area" ? AREA_COLORS[allFreqs[i2].area] : strokeColor;
        ctx.lineWidth = lineWidth;
        ctx.stroke();
      }
      ctx.setLineDash([]);

      // Dots
      for (let i = 0; i < n; i++) {
        const angle = -Math.PI / 2 + i * angleStep;
        const val = scores[allFreqs[i].area as keyof SCILScores]?.[allFreqs[i].key] ?? 0;
        const r = (val / 10) * maxRadius;
        const x = cx + r * Math.cos(angle);
        const y = cy + r * Math.sin(angle);

        ctx.beginPath();
        ctx.arc(x, y, 3.5, 0, 2 * Math.PI);
        ctx.fillStyle = strokeColor === "area" ? AREA_COLORS[allFreqs[i].area] : strokeColor;
        ctx.fill();
        ctx.strokeStyle = "#fff";
        ctx.lineWidth = 1;
        ctx.stroke();
      }
    };

    // Draw Others polygon (dashed, purple)
    drawPolygon(othersScores, "rgba(124, 58, 237, 0.08)", "#7C3AED", 2, [6, 4]);

    // Draw Self polygon (solid, navy)
    drawPolygon(selfScores, "rgba(11, 20, 55, 0.08)", "area", 2.5);

    // Draw labels
    for (let i = 0; i < n; i++) {
      const angle = -Math.PI / 2 + i * angleStep;
      const labelR = maxRadius + 28;
      const lx = cx + labelR * Math.cos(angle);
      const ly = cy + labelR * Math.sin(angle);
      ctx.fillStyle = "rgba(0,0,0,0.5)";
      ctx.font = "10px sans-serif";
      ctx.textAlign = Math.cos(angle) > 0.1 ? "left" : Math.cos(angle) < -0.1 ? "right" : "center";
      ctx.textBaseline = Math.sin(angle) > 0.1 ? "top" : Math.sin(angle) < -0.1 ? "bottom" : "middle";
      ctx.fillText(FREQ_LABELS[allFreqs[i].key] || allFreqs[i].key, lx, ly);
    }

    // Area labels
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

    // Legend
    const legendY = size - 20;
    ctx.font = "11px sans-serif";

    // Self legend
    ctx.beginPath();
    ctx.moveTo(20, legendY);
    ctx.lineTo(40, legendY);
    ctx.strokeStyle = "#0B1437";
    ctx.lineWidth = 2.5;
    ctx.setLineDash([]);
    ctx.stroke();
    ctx.fillStyle = "#0B1437";
    ctx.textAlign = "left";
    ctx.fillText("Selbstbild", 45, legendY + 4);

    // Others legend
    ctx.beginPath();
    ctx.moveTo(130, legendY);
    ctx.lineTo(150, legendY);
    ctx.strokeStyle = "#7C3AED";
    ctx.lineWidth = 2;
    ctx.setLineDash([6, 4]);
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle = "#7C3AED";
    ctx.fillText("Fremdbild", 155, legendY + 4);
  }, [selfScores, othersScores, size]);

  return (
    <div className="flex justify-center">
      <canvas ref={canvasRef} />
    </div>
  );
}
