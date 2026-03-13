"use client";

import type { TrainingPlanSummary, TodayTraining, TrainingStats } from "@/lib/types";

interface TrainingSidebarProps {
  today: TodayTraining | null;
  plans: TrainingPlanSummary[];
  stats: TrainingStats | null;
  activePlanId: string | null;
  onViewPlan: (planId: string) => void;
  onGeneratePlan: () => void;
  generating: boolean;
}

export function TrainingSidebar({
  today,
  plans,
  stats,
  activePlanId,
  onViewPlan,
  onGeneratePlan,
  generating,
}: TrainingSidebarProps) {
  const hasActivePlan = today?.has_training || plans.some((p) => p.status === "active");

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-4">
        <div className="flex items-center gap-2 mb-1">
          <svg className="w-5 h-5 text-scil" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          <h2 className="text-sm font-semibold text-white">Training</h2>
        </div>
        <p className="text-xs text-slate-500">SCIL-Mikro-Training</p>
      </div>

      {/* Stats mini */}
      {stats && (
        <div className="px-4 pb-3 grid grid-cols-2 gap-2">
          <div className="bg-white/[0.03] border border-white/[0.06] rounded-xl p-2.5">
            <div className="text-lg font-bold text-white stat-number">{stats.current_streak}</div>
            <div className="text-[10px] text-slate-500">Tage Serie</div>
          </div>
          <div className="bg-white/[0.03] border border-white/[0.06] rounded-xl p-2.5">
            <div className="text-lg font-bold text-white stat-number">{stats.total_completed_days}</div>
            <div className="text-[10px] text-slate-500">Abgeschlossen</div>
          </div>
          <div className="bg-white/[0.03] border border-white/[0.06] rounded-xl p-2.5">
            <div className="text-lg font-bold text-white stat-number">{stats.total_time_minutes}</div>
            <div className="text-[10px] text-slate-500">Minuten</div>
          </div>
          <div className="bg-white/[0.03] border border-white/[0.06] rounded-xl p-2.5">
            <div className="text-lg font-bold text-white stat-number">{stats.average_rating ? `${stats.average_rating}` : "-"}</div>
            <div className="text-[10px] text-slate-500">Bewertung</div>
          </div>
        </div>
      )}

      {/* Today mini card */}
      {today?.has_training && today.day && (
        <div className="px-4 pb-3">
          <div className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-2">Heute</div>
          <div className="bg-scil/[0.08] border border-scil/20 rounded-xl p-3">
            <div className="text-sm font-medium text-white">{today.day.title}</div>
            <div className="text-xs text-slate-400 mt-0.5">
              {today.day.content?.duration_minutes} Min. &middot;{" "}
              <span className="capitalize">{today.day.area}</span>
            </div>
            <div className="mt-1">
              <span className={`text-xs px-1.5 py-0.5 rounded-full ${
                today.day.status === "completed" ? "bg-emerald-500/10 text-emerald-400" :
                today.day.status === "in_progress" ? "bg-scil/10 text-scil" :
                "bg-amber-500/10 text-amber-400"
              }`}>
                {today.day.status === "completed" ? "Fertig" :
                 today.day.status === "in_progress" ? "In Arbeit" : "Verfuegbar"}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Plan list */}
      <div className="px-4 pb-3 flex-1 overflow-y-auto">
        <div className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-2">Plaene</div>
        {plans.length === 0 ? (
          <div className="text-center py-4">
            <p className="text-xs text-slate-500 mb-3">Noch kein Trainingsplan</p>
            <button
              onClick={onGeneratePlan}
              disabled={generating}
              className="w-full px-3 py-2 btn-glass text-white text-xs font-medium rounded-xl transition-all disabled:opacity-50"
            >
              {generating ? "Erstelle..." : "Plan erstellen"}
            </button>
          </div>
        ) : (
          <div className="space-y-1.5">
            {plans.map((plan) => {
              const isActive = plan.id === activePlanId;
              return (
                <button
                  key={plan.id}
                  onClick={() => onViewPlan(plan.id)}
                  className={`w-full text-left p-2.5 rounded-xl transition-all duration-200 ${
                    isActive
                      ? "bg-white/[0.08] text-white"
                      : "text-slate-400 hover:bg-white/[0.04] hover:text-slate-200"
                  }`}
                >
                  <div className="text-sm font-medium truncate">{plan.title}</div>
                  <div className="flex items-center justify-between mt-1">
                    <span className={`text-[10px] px-1.5 py-0.5 rounded-full ${
                      plan.status === "active" ? "bg-scil/10 text-scil" :
                      plan.status === "completed" ? "bg-emerald-500/10 text-emerald-400" :
                      "bg-slate-500/10 text-slate-400"
                    }`}>
                      {plan.status === "active" ? "Aktiv" :
                       plan.status === "completed" ? "Fertig" : plan.status}
                    </span>
                    <span className="text-[10px] text-slate-500 stat-number">
                      {Math.round(plan.overall_progress * 100)}%
                    </span>
                  </div>
                  {/* Mini progress bar */}
                  <div className="mt-1.5 h-1 bg-white/[0.03] rounded-full overflow-hidden">
                    <div
                      className="h-full bg-scil rounded-full transition-all"
                      style={{ width: `${plan.overall_progress * 100}%` }}
                    />
                  </div>
                </button>
              );
            })}
          </div>
        )}
      </div>

      {/* Generate plan button (if plans exist but no active one) */}
      {plans.length > 0 && !hasActivePlan && (
        <div className="p-4 border-t border-white/[0.06]">
          <button
            onClick={onGeneratePlan}
            disabled={generating}
            className="w-full px-3 py-2 btn-glass text-white text-xs font-medium rounded-xl transition-all disabled:opacity-50"
          >
            {generating ? "Erstelle..." : "Neuen Plan erstellen"}
          </button>
        </div>
      )}
    </div>
  );
}
