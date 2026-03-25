"use client";

import { useState, useEffect, useMemo } from "react";
import { useRouter } from "next/navigation";
import { useSessions } from "@/hooks/useSessions";
import { AppShell } from "@/components/layout/AppShell";
import { SCILPolygon } from "@/components/diagnostics/SCILPolygon";
import { JohariWindow } from "@/components/diagnostics/JohariWindow";
import type { DiagnosticResult, SCILScores, PolygonData } from "@/lib/types";

// ---------------------------------------------------------------------------
// Area configuration
// ---------------------------------------------------------------------------
const AREA_CONFIG: Record<string, { label: string; color: string; bg: string }> = {
  sensus: { label: "Sensus", color: "#E74C3C", bg: "bg-rose-500/10" },
  corpus: { label: "Corpus", color: "#F39C12", bg: "bg-amber-500/10" },
  intellektus: { label: "Intellektus", color: "#3498DB", bg: "bg-blue-500/10" },
  lingua: { label: "Lingua", color: "#2ECC71", bg: "bg-emerald-500/10" },
};

const FREQ_LABELS: Record<string, string> = {
  inner_presence: "Innere Praesenz",
  conviction: "Ueberzeugung",
  moment_focus: "Momentfokus",
  emotionality: "Emotionalitaet",
  appearance: "Erscheinung",
  gesture: "Gestik",
  facial_expression: "Mimik",
  spatial_presence: "Raumpraesenz",
  analytics: "Analytik",
  goal_orientation: "Zielorientierung",
  structure: "Struktur",
  objectivity: "Sachlichkeit",
  voice: "Stimme",
  articulation: "Artikulation",
  eloquence: "Eloquenz",
  imagery: "Bildhaftigkeit",
};

const LEVEL_LABELS: Record<string, { label: string; color: string }> = {
  low: { label: "Niedrig", color: "text-red-500" },
  moderate: { label: "Moderat", color: "text-amber-500" },
  high: { label: "Hoch", color: "text-emerald-500" },
  very_high: { label: "Sehr hoch", color: "text-blue-500" },
};

// ---------------------------------------------------------------------------
// Helper: derive Johari data from SCILScores
// ---------------------------------------------------------------------------
function deriveJohariData(scores: SCILScores): {
  public: string[];
  blind_spot: string[];
  hidden: string[];
  unknown: string[];
} {
  const publicItems: string[] = [];
  const hiddenItems: string[] = [];
  const unknownItems: string[] = [];

  for (const area of Object.keys(scores) as Array<keyof SCILScores>) {
    for (const [freq, score] of Object.entries(scores[area])) {
      const label = FREQ_LABELS[freq] || freq;
      if (score > 6) {
        publicItems.push(label);
      } else if (score >= 4) {
        hiddenItems.push(label);
      } else {
        unknownItems.push(label);
      }
    }
  }

  return {
    public: publicItems,
    blind_spot: [],
    hidden: hiddenItems,
    unknown: unknownItems,
  };
}

// ---------------------------------------------------------------------------
// Helper: compute area averages from SCILScores
// ---------------------------------------------------------------------------
function computeAreaAverages(scores: SCILScores): Record<string, number> {
  const averages: Record<string, number> = {};
  for (const area of Object.keys(scores) as Array<keyof SCILScores>) {
    const values = Object.values(scores[area]);
    if (values.length > 0) {
      averages[area] = values.reduce((a, b) => a + b, 0) / values.length;
    } else {
      averages[area] = 0;
    }
  }
  return averages;
}

// ---------------------------------------------------------------------------
// Helper: compute overall balance from area averages
// ---------------------------------------------------------------------------
function computeBalance(averages: Record<string, number>): number {
  const vals = Object.values(averages);
  if (vals.length === 0) return 0;
  const mean = vals.reduce((a, b) => a + b, 0) / vals.length;
  const maxDev = vals.reduce((max, v) => Math.max(max, Math.abs(v - mean)), 0);
  // Balance on 0-4 scale: 4 means perfectly balanced
  return Math.max(0, 4 - maxDev);
}

// ---------------------------------------------------------------------------
// Results Page
// ---------------------------------------------------------------------------
export default function ResultsPage() {
  const router = useRouter();
  const { sessions, getResult } = useSessions();

  const [selectedSessionId, setSelectedSessionId] = useState<string | null>(null);
  const [result, setResult] = useState<DiagnosticResult | null>(null);
  const [loadingResult, setLoadingResult] = useState(false);

  // Filter to only completed sessions
  const completedSessions = useMemo(
    () => sessions.filter((s) => s.status === "completed"),
    [sessions]
  );

  // Auto-select the first completed session if none selected
  useEffect(() => {
    if (!selectedSessionId && completedSessions.length > 0) {
      setSelectedSessionId(completedSessions[0].id);
    }
  }, [completedSessions, selectedSessionId]);

  // Load result when session is selected
  useEffect(() => {
    if (!selectedSessionId) {
      setResult(null);
      return;
    }

    let cancelled = false;
    setLoadingResult(true);

    getResult(selectedSessionId).then((data) => {
      if (!cancelled) {
        setResult(data);
        setLoadingResult(false);
      }
    });

    return () => {
      cancelled = true;
    };
  }, [selectedSessionId, getResult]);

  // Derived data
  const areaAverages = useMemo(
    () => (result ? computeAreaAverages(result.scores) : null),
    [result]
  );

  const balanceScore = useMemo(
    () =>
      result?.polygon_data
        ? result.polygon_data.balance_score
        : areaAverages
        ? computeBalance(areaAverages)
        : 0,
    [result, areaAverages]
  );

  const johariData = useMemo(
    () => (result ? deriveJohariData(result.scores) : null),
    [result]
  );

  // ---------------------------------------------------------------------------
  // Left sidebar: list of completed sessions
  // ---------------------------------------------------------------------------
  const leftSidebar = (
    <div className="space-y-2">
      <div className="px-1 mb-3">
        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
          Abgeschlossene Diagnostiken
        </h3>
      </div>

      {completedSessions.length === 0 ? (
        <div className="text-center py-8 px-4">
          <div className="w-10 h-10 mx-auto mb-3 rounded-xl bg-black/[0.04] flex items-center justify-center">
            <svg className="w-5 h-5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <p className="text-sm text-slate-400">
            Noch keine abgeschlossenen Diagnostiken vorhanden.
          </p>
          <button
            onClick={() => router.push("/dashboard")}
            className="mt-3 px-4 py-2 btn-glass text-white text-xs font-medium rounded-xl"
          >
            Diagnostik starten
          </button>
        </div>
      ) : (
        completedSessions.map((session) => {
          const isActive = session.id === selectedSessionId;
          const date = new Date(session.completed_at || session.created_at);
          return (
            <button
              key={session.id}
              onClick={() => setSelectedSessionId(session.id)}
              className={`w-full text-left px-3 py-3 rounded-xl transition-all ${
                isActive
                  ? "bg-scil/10 border border-scil/20"
                  : "hover:bg-black/[0.03] border border-transparent"
              }`}
            >
              <div className="flex items-center gap-2.5">
                <div
                  className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
                    isActive ? "bg-scil text-white" : "bg-black/[0.04] text-slate-400"
                  }`}
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <div className="min-w-0 flex-1">
                  <div className={`text-sm font-medium truncate ${isActive ? "text-scil" : "text-slate-700"}`}>
                    {session.title || "SCIL Diagnostik"}
                  </div>
                  <div className="text-xs text-slate-400">
                    {date.toLocaleDateString("de-DE", {
                      day: "2-digit",
                      month: "2-digit",
                      year: "numeric",
                    })}
                  </div>
                </div>
                <svg className="w-3.5 h-3.5 text-emerald-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
            </button>
          );
        })
      )}
    </div>
  );

  // ---------------------------------------------------------------------------
  // Main content
  // ---------------------------------------------------------------------------
  return (
    <AppShell leftSidebar={leftSidebar} rightDefaultOpen={false}>
      <div className="w-full px-6 py-6 max-w-5xl mx-auto">
        {/* Loading state */}
        {loadingResult && (
          <div className="flex items-center justify-center py-20">
            <div className="flex gap-1">
              <div className="w-2 h-2 rounded-full bg-scil typing-dot" />
              <div className="w-2 h-2 rounded-full bg-scil typing-dot" />
              <div className="w-2 h-2 rounded-full bg-scil typing-dot" />
            </div>
          </div>
        )}

        {/* Empty state */}
        {!loadingResult && !result && (
          <div className="flex items-center justify-center py-20 animate-fade-in-up">
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-black/[0.04] flex items-center justify-center">
                <svg className="w-8 h-8 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h2 className="text-lg font-semibold text-slate-700 mb-2">
                Keine Ergebnisse verfuegbar
              </h2>
              <p className="text-sm text-slate-400 max-w-sm">
                Schliesse eine SCIL-Diagnostik ab, um deine Ergebnisse hier einzusehen.
              </p>
              <button
                onClick={() => router.push("/dashboard")}
                className="mt-4 px-5 py-2.5 btn-glass text-white text-sm font-medium rounded-xl"
              >
                Zur Diagnostik
              </button>
            </div>
          </div>
        )}

        {/* Result content */}
        {!loadingResult && result && (
          <div className="space-y-8">
            {/* Header */}
            <div className="animate-fade-in-up">
              <h1 className="text-xl font-bold text-slate-900 mb-1">SCIL Ergebnis</h1>
              <p className="text-sm text-slate-400">
                {new Date(result.created_at).toLocaleDateString("de-DE", {
                  weekday: "long",
                  day: "2-digit",
                  month: "long",
                  year: "numeric",
                })}
              </p>
            </div>

            {/* Polygon Chart */}
            <div className="glass-card rounded-2xl p-6 animate-fade-in-up stagger-1">
              <h2 className="text-sm font-semibold text-slate-600 uppercase tracking-wider mb-4">
                Wirkungsprofil
              </h2>
              <SCILPolygon scores={result.scores} size={400} />
            </div>

            {/* Balance Score + Area Averages */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 animate-fade-in-up stagger-2">
              {/* Balance Score */}
              <div className="glass-card rounded-2xl p-6">
                <h2 className="text-sm font-semibold text-slate-600 uppercase tracking-wider mb-4">
                  Balance-Score
                </h2>
                <div className="flex items-center justify-center">
                  <div className="relative w-32 h-32">
                    <svg className="w-32 h-32 transform -rotate-90" viewBox="0 0 120 120">
                      <circle
                        cx="60"
                        cy="60"
                        r="52"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="8"
                        className="text-black/[0.06]"
                      />
                      <circle
                        cx="60"
                        cy="60"
                        r="52"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="8"
                        strokeDasharray={2 * Math.PI * 52}
                        strokeDashoffset={2 * Math.PI * 52 * (1 - balanceScore / 4)}
                        strokeLinecap="round"
                        className="text-scil transition-all duration-700"
                      />
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                      <span className="text-2xl font-bold text-slate-900 stat-number">
                        {balanceScore.toFixed(1)}
                      </span>
                      <span className="text-xs text-slate-400">von 4.0</span>
                    </div>
                  </div>
                </div>
                <p className="text-xs text-slate-400 text-center mt-3">
                  Ein hoher Balance-Score zeigt eine gleichmaessige Wirkung ueber alle Bereiche.
                </p>
              </div>

              {/* Area Averages */}
              <div className="glass-card rounded-2xl p-6">
                <h2 className="text-sm font-semibold text-slate-600 uppercase tracking-wider mb-4">
                  Bereichs-Durchschnitt
                </h2>
                <div className="space-y-4">
                  {areaAverages &&
                    Object.entries(AREA_CONFIG).map(([key, config]) => {
                      const avg = areaAverages[key] ?? 0;
                      return (
                        <div key={key}>
                          <div className="flex items-center justify-between mb-1.5">
                            <div className="flex items-center gap-2">
                              <div
                                className="w-3 h-3 rounded-full"
                                style={{ backgroundColor: config.color }}
                              />
                              <span className="text-sm font-medium text-slate-700">
                                {config.label}
                              </span>
                            </div>
                            <span className="text-sm font-semibold text-slate-900 stat-number">
                              {avg.toFixed(1)}
                            </span>
                          </div>
                          <div className="w-full bg-black/[0.04] rounded-full h-2">
                            <div
                              className="h-full rounded-full transition-all duration-700"
                              style={{
                                width: `${(avg / 10) * 100}%`,
                                backgroundColor: config.color,
                              }}
                            />
                          </div>
                        </div>
                      );
                    })}
                </div>
              </div>
            </div>

            {/* Summary */}
            {result.summary && (
              <div className="glass-card rounded-2xl p-6 animate-fade-in-up stagger-3">
                <h2 className="text-sm font-semibold text-slate-600 uppercase tracking-wider mb-4">
                  Zusammenfassung
                </h2>
                <div className="prose prose-sm max-w-none text-slate-600 leading-relaxed whitespace-pre-line">
                  {result.summary}
                </div>
              </div>
            )}

            {/* Recommendations */}
            {result.recommendations && result.recommendations.length > 0 && (
              <div className="animate-fade-in-up stagger-4">
                <h2 className="text-sm font-semibold text-slate-600 uppercase tracking-wider mb-4">
                  Empfehlungen
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {result.recommendations.map((rec, index) => {
                    const areaConfig = AREA_CONFIG[rec.area];
                    const levelInfo = LEVEL_LABELS[rec.level] || {
                      label: rec.level,
                      color: "text-slate-500",
                    };
                    return (
                      <div
                        key={`${rec.area}-${rec.frequency}-${index}`}
                        className={`glass-card rounded-2xl p-5 stagger-${Math.min(index + 1, 6)}`}
                      >
                        <div className="flex items-center gap-3 mb-3">
                          <div
                            className={`w-8 h-8 rounded-lg flex items-center justify-center ${areaConfig?.bg || "bg-slate-500/10"}`}
                          >
                            <span
                              className="text-xs font-bold"
                              style={{ color: areaConfig?.color || "#64748b" }}
                            >
                              {areaConfig?.label?.charAt(0) || "?"}
                            </span>
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="text-sm font-semibold text-slate-800 truncate">
                              {rec.label}
                            </div>
                            <div className="text-xs text-slate-400">
                              {areaConfig?.label || rec.area}
                            </div>
                          </div>
                        </div>

                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <span className="text-xs text-slate-400">Aktuell:</span>
                            <span className="text-sm font-semibold text-slate-900 stat-number">
                              {rec.current_score.toFixed(1)}
                            </span>
                          </div>
                          <span className={`text-xs font-medium ${levelInfo.color}`}>
                            {levelInfo.label}
                          </span>
                        </div>

                        {/* Score bar */}
                        <div className="mt-2 w-full bg-black/[0.04] rounded-full h-1.5">
                          <div
                            className="h-full rounded-full transition-all duration-500"
                            style={{
                              width: `${(rec.current_score / 10) * 100}%`,
                              backgroundColor: areaConfig?.color || "#64748b",
                            }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Johari Window */}
            {johariData && (
              <div className="glass-card rounded-2xl p-6 animate-fade-in-up stagger-5">
                <JohariWindow
                  data={johariData}
                  competencyLabels={Object.fromEntries(
                    Object.values(FREQ_LABELS).map((label) => [label, label])
                  )}
                />
              </div>
            )}
          </div>
        )}
      </div>
    </AppShell>
  );
}
