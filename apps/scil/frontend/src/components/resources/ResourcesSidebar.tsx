"use client";

import type { DiagnosticCode } from "@/lib/types";

interface ResourcesSidebarProps {
  codes: DiagnosticCode[];
  activeTab: string;
  onTabChange: (tab: string) => void;
  purchaseCount: number;
}

const FILTER_TABS = [
  { key: "codes", label: "Codes" },
  { key: "trainings", label: "Trainings" },
  { key: "books", label: "Buecher" },
] as const;

export function ResourcesSidebar({
  codes,
  activeTab,
  onTabChange,
  purchaseCount,
}: ResourcesSidebarProps) {
  const activeCodes = codes.filter((c) =>
    ["emitted", "sold", "activated"].includes(c.status)
  );

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-4">
        <div className="flex items-center gap-2 mb-1">
          <svg
            className="w-5 h-5 text-scil"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"
            />
          </svg>
          <h2 className="text-sm font-semibold text-slate-900">Ressourcen</h2>
        </div>
        <p className="text-xs text-slate-400">
          Codes, Trainings &amp; Materialien
        </p>
      </div>

      {/* Purchase history summary */}
      <div className="px-4 pb-3">
        <div className="bg-black/[0.02] border border-black/[0.06] rounded-xl p-3">
          <div className="flex items-center gap-2 mb-2">
            <svg
              className="w-4 h-4 text-slate-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
              />
            </svg>
            <span className="text-xs font-medium text-slate-900">
              Kaufhistorie
            </span>
          </div>
          <p className="text-xs text-slate-500">
            {purchaseCount > 0
              ? `${purchaseCount} Kaeufe insgesamt`
              : "Noch keine Kaeufe"}
          </p>
        </div>
      </div>

      {/* Quick filter buttons */}
      <div className="px-4 pb-3">
        <div className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-2">
          Schnellfilter
        </div>
        <div className="flex flex-col gap-1.5">
          {FILTER_TABS.map((tab) => (
            <button
              key={tab.key}
              onClick={() => onTabChange(tab.key)}
              className={`w-full text-left px-3 py-2 text-xs font-medium rounded-full transition-all ${
                activeTab === tab.key
                  ? "bg-scil text-white"
                  : "bg-black/[0.02] text-slate-500 border border-black/[0.06] hover:bg-black/[0.04]"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Stats */}
      <div className="px-4 pb-3">
        <div className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-2">
          Uebersicht
        </div>
        <div className="bg-black/[0.02] border border-black/[0.06] rounded-xl p-3 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-500">Gesamte Kaeufe</span>
            <span className="text-sm font-bold text-slate-900 stat-number">
              {purchaseCount}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-500">Aktive Codes</span>
            <span className="text-sm font-bold text-emerald-400 stat-number">
              {activeCodes.length}
            </span>
          </div>
        </div>
      </div>

      <div className="flex-1" />
    </div>
  );
}
