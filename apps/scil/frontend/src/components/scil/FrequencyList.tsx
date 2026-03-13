"use client";

import type { PolygonData } from "@/lib/types";

interface FrequencyListProps {
  polygon: PolygonData;
}

const LEVEL_COLORS: Record<string, string> = {
  a: "text-green-400",
  b: "text-blue-400",
  c: "text-slate-300",
  d: "text-yellow-400",
  e: "text-red-400",
};

export function FrequencyList({ polygon }: FrequencyListProps) {
  return (
    <div className="bg-surface rounded-xl p-3">
      <div className="text-xs text-slate-400 mb-3">16-Frequenz Detail</div>
      <div className="space-y-3">
        {Object.entries(polygon.areas).map(([areaKey, area]) => (
          <div key={areaKey}>
            <div className="flex items-center gap-1.5 mb-1.5">
              <div
                className="w-2 h-2 rounded-full"
                style={{ backgroundColor: area.color }}
              />
              <span className="text-xs font-medium" style={{ color: area.color }}>
                {area.label}
              </span>
            </div>
            <div className="space-y-1 pl-3.5">
              {Object.entries(area.frequencies).map(([freqKey, freq]) => (
                <div key={freqKey} className="flex items-center gap-2 text-xs">
                  <span className="text-slate-400 flex-1 truncate">{freq.label}</span>
                  <div className="w-16 bg-surface-dark rounded-full h-1">
                    <div
                      className="h-full rounded-full"
                      style={{
                        width: `${(freq.score / 4) * 100}%`,
                        backgroundColor: area.color,
                      }}
                    />
                  </div>
                  <span className="text-slate-300 w-6 text-right">
                    {freq.score.toFixed(1)}
                  </span>
                  <span className={`w-3 font-mono ${LEVEL_COLORS[freq.level] || "text-slate-500"}`}>
                    {freq.level}
                  </span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
