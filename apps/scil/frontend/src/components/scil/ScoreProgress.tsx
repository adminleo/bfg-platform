"use client";

import type { ClusterProgress } from "@/lib/types";

interface ScoreProgressProps {
  progress: number;
  isComplete: boolean;
  clusterProgress: ClusterProgress | null;
  totalScored: number;
}

const CLUSTER_CONFIG = [
  { key: "sensus" as const, label: "S", fullLabel: "Sensus", color: "#E74C3C" },
  { key: "corpus" as const, label: "C", fullLabel: "Corpus", color: "#F39C12" },
  { key: "intellektus" as const, label: "I", fullLabel: "Intellektus", color: "#3498DB" },
  { key: "lingua" as const, label: "L", fullLabel: "Lingua", color: "#2ECC71" },
];

export function ScoreProgress({
  progress,
  isComplete,
  clusterProgress,
  totalScored,
}: ScoreProgressProps) {
  // Fallback for legacy mode (no cluster progress yet)
  if (!clusterProgress) {
    const questionCount = Math.round(progress * 100);
    return (
      <div className="bg-surface rounded-xl p-3">
        <div className="flex justify-between items-center mb-2">
          <span className="text-xs text-slate-400">Fortschritt</span>
          <span className="text-xs text-slate-300">
            {isComplete ? "Abgeschlossen" : `${questionCount}/100 Items`}
          </span>
        </div>
        <div className="w-full bg-surface-dark rounded-full h-2">
          <div
            className={`h-full rounded-full transition-all duration-700 ease-out ${
              isComplete ? "bg-green-500" : "bg-scil"
            }`}
            style={{ width: `${Math.min(progress * 100, 100)}%` }}
          />
        </div>
      </div>
    );
  }

  return (
    <div className="bg-surface rounded-xl p-3 space-y-3">
      {/* Overall progress */}
      <div className="flex justify-between items-center">
        <span className="text-xs text-slate-400">Fortschritt</span>
        <span className="text-xs text-slate-300 font-medium">
          {isComplete ? (
            <span className="text-green-400">Abgeschlossen</span>
          ) : (
            `${totalScored}/100 Items`
          )}
        </span>
      </div>

      {/* Overall bar */}
      <div className="w-full bg-surface-dark rounded-full h-1.5">
        <div
          className={`h-full rounded-full transition-all duration-700 ease-out ${
            isComplete ? "bg-green-500" : "bg-scil"
          }`}
          style={{ width: `${Math.min(progress * 100, 100)}%` }}
        />
      </div>

      {/* Per-cluster progress */}
      <div className="space-y-2 pt-1">
        {CLUSTER_CONFIG.map(({ key, label, fullLabel, color }) => {
          const cp = clusterProgress[key];
          const answered = cp?.answered ?? 0;
          const total = cp?.total ?? 25;
          const pct = total > 0 ? (answered / total) * 100 : 0;
          const isDone = answered >= total;

          return (
            <div key={key} className="flex items-center gap-2">
              <div
                className="w-5 h-5 rounded flex items-center justify-center text-[10px] font-bold text-white flex-shrink-0"
                style={{ backgroundColor: color }}
              >
                {label}
              </div>
              <div className="flex-1">
                <div className="flex justify-between items-center mb-0.5">
                  <span className="text-[10px] text-slate-400">{fullLabel}</span>
                  <span className="text-[10px] text-slate-500">
                    {isDone ? (
                      <span className="text-green-400">&#10003;</span>
                    ) : (
                      `${answered}/${total}`
                    )}
                  </span>
                </div>
                <div className="w-full bg-surface-dark rounded-full h-1">
                  <div
                    className="h-full rounded-full transition-all duration-500 ease-out"
                    style={{
                      width: `${Math.min(pct, 100)}%`,
                      backgroundColor: isDone ? "#22c55e" : color,
                    }}
                  />
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
