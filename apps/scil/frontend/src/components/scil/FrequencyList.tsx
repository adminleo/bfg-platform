"use client";

import { useState } from "react";
import type { PolygonData, SCILScores } from "@/lib/types";

interface FrequencyListProps {
  polygon?: PolygonData | null;
  scores?: SCILScores | null;
}

const AREA_CONFIG: Record<string, { label: string; color: string; bgLight: string }> = {
  sensus: { label: "Sensus", color: "#E74C3C", bgLight: "rgba(231,76,60,0.06)" },
  corpus: { label: "Corpus", color: "#F39C12", bgLight: "rgba(243,156,18,0.06)" },
  intellektus: { label: "Intellektus", color: "#3498DB", bgLight: "rgba(52,152,219,0.06)" },
  lingua: { label: "Lingua", color: "#2ECC71", bgLight: "rgba(46,204,113,0.06)" },
};

const FREQ_FULL_LABELS: Record<string, string> = {
  innere_praesenz: "Innere Praesenz",
  innere_ueberzeugung: "Innere Ueberzeugung",
  prozessfokussierung: "Prozessfokussierung",
  emotionalitaet: "Emotionalitaet",
  erscheinungsbild: "Erscheinungsbild",
  mimik: "Mimik",
  gestik: "Gestik",
  raeumliche_praesenz: "Raeumliche Praesenz",
  sachlichkeit: "Sachlichkeit",
  analytik: "Analytik",
  struktur: "Struktur",
  zielorientierung: "Zielorientierung",
  stimme: "Stimme",
  artikulation: "Artikulation",
  beredsamkeit: "Beredsamkeit",
  bildhaftigkeit: "Bildhaftigkeit",
};

const LEVEL_COLORS: Record<string, { text: string; bg: string; label: string }> = {
  a: { text: "text-green-600", bg: "bg-green-50", label: "Sehr hoch" },
  b: { text: "text-blue-600", bg: "bg-blue-50", label: "Hoch" },
  c: { text: "text-slate-500", bg: "bg-slate-50", label: "Mittel" },
  d: { text: "text-amber-600", bg: "bg-amber-50", label: "Niedrig" },
  e: { text: "text-red-500", bg: "bg-red-50", label: "Sehr niedrig" },
};

export function FrequencyList({ polygon, scores }: FrequencyListProps) {
  const [expandedAreas, setExpandedAreas] = useState<Record<string, boolean>>({});

  const toggleArea = (area: string) => {
    setExpandedAreas((prev) => ({ ...prev, [area]: !prev[area] }));
  };

  // Build frequency data from polygon (rich data) or fall back to raw scores
  const areas = polygon
    ? Object.entries(polygon.areas)
    : scores
    ? (Object.entries(scores) as [string, Record<string, number>][]).map(([key, freqs]) => {
        const cfg = AREA_CONFIG[key] || { label: key, color: "#94a3b8", bgLight: "rgba(148,163,184,0.06)" };
        const vals = Object.values(freqs);
        return [
          key,
          {
            label: cfg.label,
            color: cfg.color,
            average: vals.reduce((a, b) => a + b, 0) / Math.max(vals.length, 1),
            frequencies: Object.fromEntries(
              Object.entries(freqs).map(([fk, fv]) => [
                fk,
                {
                  score: fv,
                  label: FREQ_FULL_LABELS[fk] || fk,
                  level: fv >= 3.2 ? "a" : fv >= 2.4 ? "b" : fv >= 1.6 ? "c" : fv >= 0.8 ? "d" : "e",
                  level_label: "",
                },
              ])
            ),
          },
        ] as const;
      })
    : [];

  if (areas.length === 0) return null;

  return (
    <div className="space-y-2">
      <div className="text-xs text-slate-500 font-medium px-1">
        Cluster-Analyse (16 Frequenzen)
      </div>
      {areas.map(([areaKey, area]) => {
        const isExpanded = expandedAreas[areaKey as string] ?? false;
        const cfg = AREA_CONFIG[areaKey as string] || { label: areaKey, color: "#94a3b8", bgLight: "rgba(148,163,184,0.06)" };
        const freqEntries = Object.entries(area.frequencies);
        const freqCount = freqEntries.length;

        return (
          <div
            key={areaKey as string}
            className="rounded-xl border border-black/[0.06] overflow-hidden transition-all duration-200"
          >
            {/* Cluster Header — clickable to expand */}
            <button
              onClick={() => toggleArea(areaKey as string)}
              className="w-full flex items-center gap-2.5 px-3 py-2.5 hover:bg-black/[0.02] transition-colors"
            >
              {/* Color dot */}
              <div
                className="w-3 h-3 rounded-md flex-shrink-0"
                style={{ backgroundColor: cfg.color }}
              />
              {/* Area label */}
              <span className="text-sm font-semibold text-slate-800 flex-1 text-left">
                {area.label}
              </span>
              {/* Average score */}
              <div className="flex items-center gap-1.5 mr-1">
                <div className="w-12 bg-black/[0.04] rounded-full h-1.5">
                  <div
                    className="h-full rounded-full transition-all duration-500"
                    style={{
                      width: `${(area.average / 4) * 100}%`,
                      backgroundColor: cfg.color,
                    }}
                  />
                </div>
                <span
                  className="text-xs font-bold w-7 text-right"
                  style={{ color: cfg.color }}
                >
                  {area.average.toFixed(1)}
                </span>
              </div>
              {/* Frequency count badge */}
              <span className="text-[10px] text-slate-500 mr-0.5">
                {freqCount}
              </span>
              {/* Chevron */}
              <svg
                className={`w-3.5 h-3.5 text-slate-500 transition-transform duration-200 ${
                  isExpanded ? "rotate-180" : ""
                }`}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {/* Expanded Frequency List */}
            {isExpanded && (
              <div
                className="border-t border-black/[0.04] px-3 py-2 space-y-1"
                style={{ backgroundColor: cfg.bgLight }}
              >
                {/* Column headers */}
                <div className="flex items-center gap-2 text-[10px] text-slate-500 pb-1 border-b border-black/[0.04] mb-1">
                  <span className="flex-1">Frequenz</span>
                  <span className="w-16 text-center">Score</span>
                  <span className="w-10 text-center">Level</span>
                </div>

                {freqEntries.map(([freqKey, freq]) => {
                  const levelCfg = LEVEL_COLORS[freq.level] || { text: "text-slate-500", bg: "bg-slate-50", label: "-" };
                  return (
                    <div
                      key={freqKey}
                      className="flex items-center gap-2 py-1 group"
                    >
                      {/* Frequency name */}
                      <span className="text-xs text-slate-600 flex-1">
                        {freq.label || FREQ_FULL_LABELS[freqKey] || freqKey}
                      </span>
                      {/* Score bar + value */}
                      <div className="flex items-center gap-1.5 w-16">
                        <div className="flex-1 bg-black/[0.04] rounded-full h-1.5">
                          <div
                            className="h-full rounded-full transition-all duration-500"
                            style={{
                              width: `${(freq.score / 4) * 100}%`,
                              backgroundColor: cfg.color,
                            }}
                          />
                        </div>
                        <span className="text-[11px] font-semibold text-slate-700 w-6 text-right tabular-nums">
                          {freq.score.toFixed(1)}
                        </span>
                      </div>
                      {/* Level badge */}
                      <span
                        className={`text-[10px] font-bold w-10 text-center py-0.5 rounded ${levelCfg.bg} ${levelCfg.text}`}
                      >
                        {freq.level.toUpperCase()}
                      </span>
                    </div>
                  );
                })}

                {/* Cluster average footer */}
                <div className="flex items-center gap-2 pt-1.5 mt-1 border-t border-black/[0.04]">
                  <span className="text-[11px] font-medium text-slate-500 flex-1">
                    Durchschnitt
                  </span>
                  <span
                    className="text-[11px] font-bold"
                    style={{ color: cfg.color }}
                  >
                    = {freqEntries.length > 0
                      ? (freqEntries.reduce((s, [, f]) => s + f.score, 0) / freqEntries.length).toFixed(2)
                      : "—"}
                  </span>
                  <span className="text-[10px] text-slate-500 w-10 text-center">
                    / 4.0
                  </span>
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
