"use client";

import { useEffect, useState } from "react";
import { SCILPolygon } from "@/components/scil/SCILPolygon";
import { ScoreProgress } from "@/components/scil/ScoreProgress";
import { FrequencyList } from "@/components/scil/FrequencyList";
import { ResultSummary } from "@/components/scil/ResultSummary";
import type { SCILScores, PolygonData, ClusterProgress, DiagnosticResult } from "@/lib/types";

interface RightSidebarProps {
  scores: SCILScores | null;
  polygon: PolygonData | null;
  progress: number;
  isComplete: boolean;
  resultId: string | null;
  sessionId: string | null;
  clusterProgress: ClusterProgress | null;
  totalScored: number;
}

export function RightSidebar({
  scores,
  polygon,
  progress,
  isComplete,
  resultId,
  sessionId,
  clusterProgress,
  totalScored,
}: RightSidebarProps) {
  const [result, setResult] = useState<DiagnosticResult | null>(null);

  // Load result when complete
  useEffect(() => {
    if (isComplete && resultId && sessionId) {
      import("@/lib/api").then(({ api }) => {
        api
          .get<DiagnosticResult>(`/scil/sessions/${sessionId}/result`)
          .then(setResult)
          .catch(console.error);
      });
    }
  }, [isComplete, resultId, sessionId]);

  return (
    <div className="flex flex-col h-full bg-white/80 p-4">
      {/* Header */}
      <div className="mb-4">
        <h2 className="text-sm font-semibold text-slate-600 uppercase tracking-wider">
          SCIL Wirkungsprofil
        </h2>
      </div>

      {!scores && !polygon ? (
        /* Empty state */
        <div className="flex-1 flex items-center justify-center text-center text-slate-400 px-4">
          <div>
            <div className="text-4xl mb-3 animate-float">&#x1F98E;</div>
            <p className="text-sm">
              Dein Wirkungsprofil erscheint hier, sobald die Diagnostik beginnt.
            </p>
          </div>
        </div>
      ) : (
        <div className="flex-1 overflow-y-auto space-y-4">
          {/* Polygon */}
          {scores && (
            <div className="bg-black/[0.02] border border-black/[0.06] rounded-2xl p-3">
              <SCILPolygon scores={scores} size={280} />
            </div>
          )}

          {/* Progress */}
          <ScoreProgress
            progress={progress}
            isComplete={isComplete}
            clusterProgress={clusterProgress}
            totalScored={totalScored}
          />

          {/* Balance Score */}
          {polygon && (
            <div className="bg-black/[0.02] border border-black/[0.06] rounded-2xl p-3">
              <div className="flex justify-between items-center">
                <span className="text-xs text-slate-500">Balance-Score</span>
                <span className="text-lg font-bold text-scil stat-number">
                  {polygon.balance_score.toFixed(1)}/4.0
                </span>
              </div>
            </div>
          )}

          {/* Area Averages */}
          {polygon && (
            <div className="bg-black/[0.02] border border-black/[0.06] rounded-2xl p-3 space-y-2">
              <div className="text-xs text-slate-500 mb-2">Bereichs-Durchschnitt</div>
              {Object.entries(polygon.areas).map(([key, area]) => (
                <div key={key} className="flex items-center gap-2">
                  <div
                    className="w-2 h-2 rounded-full"
                    style={{ backgroundColor: area.color }}
                  />
                  <span className="text-xs text-slate-600 flex-1">{area.label}</span>
                  <div className="flex-1 bg-black/[0.02] rounded-full h-1.5">
                    <div
                      className="h-full rounded-full transition-all duration-500"
                      style={{
                        width: `${(area.average / 4) * 100}%`,
                        backgroundColor: area.color,
                      }}
                    />
                  </div>
                  <span className="text-xs text-slate-500 w-8 text-right stat-number">
                    {area.average.toFixed(1)}
                  </span>
                </div>
              ))}
            </div>
          )}

          {/* Frequency Details (when complete) */}
          {isComplete && polygon && <FrequencyList polygon={polygon} />}

          {/* Result Summary (when complete) */}
          {isComplete && result && <ResultSummary result={result} />}
        </div>
      )}
    </div>
  );
}
