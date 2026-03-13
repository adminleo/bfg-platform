"use client";

import type { CoacheeListItem, CoachDashboardStats } from "@/lib/types";

const STATUS_LABELS: Record<string, { label: string; color: string }> = {
  invited: { label: "Eingeladen", color: "text-blue-400" },
  pending: { label: "Ausstehend", color: "text-yellow-400" },
  active: { label: "Aktiv", color: "text-scil" },
  completed: { label: "Abgeschlossen", color: "text-emerald-400" },
  archived: { label: "Archiviert", color: "text-slate-500" },
};

interface CoachSidebarProps {
  stats: CoachDashboardStats | null;
  coachees: CoacheeListItem[];
  selectedId: string | null;
  onSelectCoachee: (id: string) => void;
  onInvite: () => void;
}

export function CoachSidebar({
  stats,
  coachees,
  selectedId,
  onSelectCoachee,
  onInvite,
}: CoachSidebarProps) {
  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-4">
        <div className="flex items-center gap-2 mb-1">
          <svg className="w-5 h-5 text-scil" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          <h2 className="text-sm font-semibold text-white">Coach Dashboard</h2>
        </div>
      </div>

      {/* Stats mini */}
      {stats && (
        <div className="px-4 pb-3 grid grid-cols-2 gap-2">
          <div className="bg-surface rounded-lg p-2.5 border border-border">
            <div className="text-lg font-bold text-white">{stats.total_coachees}</div>
            <div className="text-[10px] text-slate-500">Coachees</div>
          </div>
          <div className="bg-surface rounded-lg p-2.5 border border-border">
            <div className="text-lg font-bold text-scil">{stats.active_diagnostics}</div>
            <div className="text-[10px] text-slate-500">Aktive Diag.</div>
          </div>
          <div className="bg-surface rounded-lg p-2.5 border border-border">
            <div className="text-lg font-bold text-emerald-400">{stats.codes_available}</div>
            <div className="text-[10px] text-slate-500">Codes</div>
          </div>
          <div className="bg-surface rounded-lg p-2.5 border border-border">
            <div className="text-lg font-bold text-blue-400">{stats.completed_diagnostics}</div>
            <div className="text-[10px] text-slate-500">Abgeschl.</div>
          </div>
        </div>
      )}

      {/* Coachee list */}
      <div className="px-4 pb-3 flex-1 overflow-y-auto">
        <div className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-2">Coachees</div>
        {coachees.length === 0 ? (
          <div className="text-center py-4">
            <p className="text-xs text-slate-500 mb-3">Noch keine Coachees</p>
          </div>
        ) : (
          <div className="space-y-1">
            {coachees.map((c) => {
              const statusInfo = STATUS_LABELS[c.status] || { label: c.status, color: "text-slate-400" };
              const isSelected = selectedId === c.id;
              return (
                <button
                  key={c.id}
                  onClick={() => onSelectCoachee(c.id)}
                  className={`w-full text-left flex items-center gap-2.5 p-2 rounded-lg transition-colors ${
                    isSelected
                      ? "bg-scil/10 border border-scil/30"
                      : "hover:bg-surface border border-transparent"
                  }`}
                >
                  <div className="w-7 h-7 rounded-full bg-surface-dark flex items-center justify-center text-slate-400 text-xs font-medium flex-shrink-0">
                    {(c.coachee_name || c.coachee_email).charAt(0).toUpperCase()}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-xs font-medium text-white truncate">
                      {c.coachee_name || c.coachee_email}
                    </div>
                    <div className="flex items-center gap-1.5">
                      <span className={`text-[10px] ${statusInfo.color}`}>{statusInfo.label}</span>
                      {c.has_diagnostic && (
                        <span className="text-[10px] text-scil">&#x25CF;</span>
                      )}
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        )}
      </div>

      {/* Invite button */}
      <div className="p-4 border-t border-border">
        <button
          onClick={onInvite}
          className="w-full flex items-center justify-center gap-2 px-3 py-2 bg-scil hover:bg-scil-dark text-white text-xs font-medium rounded-lg transition-colors"
        >
          <span className="text-sm">+</span>
          Coachee einladen
        </button>
      </div>
    </div>
  );
}
