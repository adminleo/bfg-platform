"use client";

import { useState } from "react";
import { useDailyTraining } from "@/hooks/useDailyTraining";
import { AppShell } from "@/components/layout/AppShell";
import { TrainingSidebar } from "@/components/training/TrainingSidebar";
import type { TrainingDay } from "@/lib/types";

// ---------------------------------------------------------------------------
// Area config
// ---------------------------------------------------------------------------
const AREA_CONFIG: Record<string, { label: string; color: string; icon: string }> = {
  sensus: { label: "Sensus", color: "text-rose-400", icon: "S" },
  corpus: { label: "Corpus", color: "text-amber-400", icon: "C" },
  intellektus: { label: "Intellektus", color: "text-blue-400", icon: "I" },
  lingua: { label: "Lingua", color: "text-emerald-400", icon: "L" },
  general: { label: "Allgemein", color: "text-slate-400", icon: "G" },
};

const AREA_BG: Record<string, string> = {
  sensus: "bg-rose-500/20",
  corpus: "bg-amber-500/20",
  intellektus: "bg-blue-500/20",
  lingua: "bg-emerald-500/20",
  general: "bg-slate-500/20",
};

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function ProgressRing({ progress, size = 64 }: { progress: number; size?: number }) {
  const strokeWidth = 4;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - progress * circumference;

  return (
    <svg width={size} height={size} className="transform -rotate-90">
      <circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        fill="none"
        stroke="currentColor"
        strokeWidth={strokeWidth}
        className="text-black/[0.06]"
      />
      <circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        fill="none"
        stroke="currentColor"
        strokeWidth={strokeWidth}
        strokeDasharray={circumference}
        strokeDashoffset={offset}
        strokeLinecap="round"
        className="text-scil transition-all duration-500"
      />
    </svg>
  );
}

function DayCard({
  day,
  onStart,
  onComplete,
  isActive,
  className = "",
}: {
  day: TrainingDay;
  onStart: () => void;
  onComplete: () => void;
  isActive: boolean;
  className?: string;
}) {
  const area = AREA_CONFIG[day.area] || AREA_CONFIG.general;
  const areaBg = AREA_BG[day.area] || AREA_BG.general;
  const isLocked = day.status === "locked";
  const isCompleted = day.status === "completed";
  const isAvailable = day.status === "available";
  const isInProgress = day.status === "in_progress";

  return (
    <div
      className={`glass-card-interactive p-4 rounded-2xl transition-all ${
        isActive
          ? "border-scil ring-1 ring-scil/30"
          : isCompleted
          ? "border-emerald-500/30"
          : isLocked
          ? "opacity-50"
          : ""
      } ${className}`}
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className={`w-8 h-8 rounded-lg ${areaBg} flex items-center justify-center ${area.color} font-bold text-sm`}>
            {area.icon}
          </div>
          <div>
            <div className="text-sm font-medium text-slate-900">{day.title}</div>
            <div className="text-xs text-slate-400">
              Woche {day.week_number}, Tag {day.day_number}
              {day.content && ` \u00B7 ${day.content.duration_minutes} Min.`}
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {isCompleted && (
            <span className="text-xs font-medium text-emerald-400 bg-emerald-500/10 px-2 py-1 rounded-full">
              Fertig
            </span>
          )}
          {isInProgress && (
            <span className="text-xs font-medium text-scil bg-scil/10 px-2 py-1 rounded-full">
              In Arbeit
            </span>
          )}
          {isLocked && (
            <svg className="w-4 h-4 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          )}
        </div>
      </div>

      {day.coaching_note && !isLocked && (
        <p className="text-xs text-slate-500 mb-3 italic">
          {day.coaching_note}
        </p>
      )}

      {day.content && !isLocked && (
        <div className="mb-3">
          <span className={`inline-block text-xs px-2 py-0.5 rounded-full ${areaBg} ${area.color}`}>
            {day.content.content_type === "exercise" ? "Uebung" :
             day.content.content_type === "reflection" ? "Reflexion" :
             day.content.content_type === "article" ? "Artikel" :
             day.content.content_type === "video" ? "Video" : "Quiz"}
          </span>
          <p className="text-xs text-slate-500 mt-1">{day.content.description}</p>
        </div>
      )}

      {isAvailable && (
        <button
          onClick={onStart}
          className="w-full py-2 btn-glass text-white text-sm font-medium rounded-xl transition-colors"
        >
          Training starten
        </button>
      )}
      {isInProgress && (
        <button
          onClick={onComplete}
          className="w-full py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-medium rounded-xl transition-colors"
        >
          Als fertig markieren
        </button>
      )}

      {day.progress?.ai_feedback && (
        <div className="mt-3 p-3 bg-scil/5 border border-scil/20 rounded-xl">
          <div className="text-xs text-scil font-medium mb-1">Coach-Feedback</div>
          <p className="text-xs text-slate-600">{day.progress.ai_feedback}</p>
        </div>
      )}
    </div>
  );
}

function CompletionModal({
  day,
  onClose,
  onSubmit,
  isSubmitting,
}: {
  day: TrainingDay;
  onClose: () => void;
  onSubmit: (reflection: string, rating: number) => void;
  isSubmitting: boolean;
}) {
  const [reflection, setReflection] = useState("");
  const [rating, setRating] = useState(0);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(reflection, rating);
  };

  return (
    <div className="fixed inset-0 modal-backdrop flex items-center justify-center z-50 p-4">
      <div className="glass-strong rounded-2xl max-w-md w-full p-6 animate-fade-in-up">
        <h3 className="text-lg font-semibold text-slate-900 mb-1">Training abschliessen</h3>
        <p className="text-sm text-slate-500 mb-4">{day.title}</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          {day.content?.body && (
            <div className="p-3 bg-black/[0.02] border border-black/[0.06] rounded-xl">
              {day.content.content_type === "reflection" && Array.isArray(day.content.body.prompts) && (
                <div className="space-y-1">
                  <div className="text-xs text-scil font-medium mb-2">Reflexionsfragen:</div>
                  {(day.content.body.prompts as string[]).map((p: string, i: number) => (
                    <p key={i} className="text-xs text-slate-500">{`\u2022 ${p}`}</p>
                  ))}
                </div>
              )}
              {day.content.content_type === "exercise" && typeof day.content.body.reflection_prompt === "string" && (
                <p className="text-xs text-slate-500">
                  {String(day.content.body.reflection_prompt)}
                </p>
              )}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-slate-500 mb-1">
              Deine Reflexion (optional)
            </label>
            <textarea
              value={reflection}
              onChange={(e) => setReflection(e.target.value)}
              rows={4}
              placeholder="Was hast du gelernt? Wie fuehlt es sich an?"
              className="w-full px-3 py-2.5 bg-white border border-black/[0.06] rounded-xl
                         text-slate-900 placeholder-slate-400 focus:outline-none focus:border-scil resize-none"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-500 mb-2">
              Wie hilfreich war diese Einheit?
            </label>
            <div className="flex gap-2">
              {[1, 2, 3, 4, 5].map((n) => (
                <button
                  key={n}
                  type="button"
                  onClick={() => setRating(n)}
                  className={`w-10 h-10 rounded-xl border transition-colors font-medium text-sm ${
                    n <= rating
                      ? "bg-scil border-scil text-white"
                      : "bg-white border-black/[0.06] text-slate-500 hover:border-scil/50"
                  }`}
                >
                  {n}
                </button>
              ))}
            </div>
          </div>

          <div className="flex gap-3">
            <button
              type="submit"
              disabled={isSubmitting}
              className="flex-1 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-medium
                         rounded-xl transition-colors disabled:opacity-50"
            >
              {isSubmitting ? "Wird gespeichert..." : "Abschliessen"}
            </button>
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2.5 btn-ghost text-slate-600 text-sm rounded-xl"
            >
              Abbrechen
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main Page
// ---------------------------------------------------------------------------

export default function TrainingPage() {
  const {
    today,
    plans,
    activePlan,
    stats,
    isLoading,
    error,
    generatePlan,
    startDay,
    completeDay,
    fetchPlanDetail,
  } = useDailyTraining();

  const [showCompletion, setShowCompletion] = useState<TrainingDay | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [generating, setGenerating] = useState(false);

  const handleGeneratePlan = async () => {
    setGenerating(true);
    await generatePlan();
    setGenerating(false);
  };

  const handleStartDay = async (dayId: string) => {
    await startDay(dayId);
  };

  const handleOpenCompletion = (day: TrainingDay) => {
    setShowCompletion(day);
  };

  const handleCompleteDay = async (reflection: string, rating: number) => {
    if (!showCompletion) return;
    setSubmitting(true);
    await completeDay(showCompletion.id, reflection, rating);
    setSubmitting(false);
    setShowCompletion(null);
  };

  const handleViewPlan = async (planId: string) => {
    await fetchPlanDetail(planId);
  };

  const hasActivePlan = today?.has_training || plans.some((p) => p.status === "active");

  return (
    <>
      <AppShell
        leftSidebar={
          <TrainingSidebar
            today={today}
            plans={plans}
            stats={stats}
            activePlanId={activePlan?.id || null}
            onViewPlan={handleViewPlan}
            onGeneratePlan={handleGeneratePlan}
            generating={generating}
          />
        }
        rightDefaultOpen={false}
      >
        <div className="w-full px-6 py-6">
          {isLoading && (
            <div className="flex items-center justify-center py-12">
              <div className="flex gap-1">
                <div className="w-2 h-2 rounded-full bg-scil typing-dot" />
                <div className="w-2 h-2 rounded-full bg-scil typing-dot" />
                <div className="w-2 h-2 rounded-full bg-scil typing-dot" />
              </div>
            </div>
          )}

          {error && (
            <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-sm animate-fade-in-up">
              {error}
            </div>
          )}

          {/* Today's Training */}
          {today?.has_training && today.day && (
            <div className="mb-8 animate-fade-in-up">
              <h2 className="text-lg font-semibold text-slate-900 mb-4">Heute</h2>
              <DayCard
                day={today.day}
                isActive={true}
                onStart={() => handleStartDay(today.day!.id)}
                onComplete={() => handleOpenCompletion(today.day!)}
              />
            </div>
          )}

          {/* No Plan State */}
          {!isLoading && !hasActivePlan && (
            <div className="glass-card rounded-2xl p-8 text-center mb-8 animate-fade-in-up">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-scil/20 flex items-center justify-center">
                <svg className="w-8 h-8 text-scil" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <h2 className="text-xl font-bold text-slate-900 mb-2">Starte dein SCIL-Training</h2>
              <p className="text-slate-500 text-sm mb-6 max-w-md mx-auto">
                Basierend auf deinen SCIL-Ergebnissen erstellen wir einen personalisierten
                4-Wochen-Trainingsplan mit taeglichen Mikro-Einheiten.
              </p>
              <button
                onClick={handleGeneratePlan}
                disabled={generating}
                className="px-6 py-2.5 btn-glass text-white font-medium
                           rounded-xl transition-colors disabled:opacity-50"
              >
                {generating ? "Plan wird erstellt..." : "Trainingsplan erstellen"}
              </button>
            </div>
          )}

          {/* Active Plan Overview */}
          {activePlan && (
            <div className="mb-8 animate-fade-in-up">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-slate-900">{activePlan.title}</h2>
                <div className="flex items-center gap-3">
                  <div className="relative">
                    <ProgressRing progress={activePlan.overall_progress} />
                    <div className="absolute inset-0 flex items-center justify-center">
                      <span className="text-xs font-bold text-slate-900 stat-number">
                        {Math.round(activePlan.overall_progress * 100)}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {activePlan.ai_rationale && (
                <div className="mb-4 p-3 bg-scil/5 border border-scil/20 rounded-xl">
                  <p className="text-sm text-slate-600">{activePlan.ai_rationale}</p>
                </div>
              )}

              {/* Week Tabs */}
              {Array.from({ length: activePlan.total_weeks }, (_, i) => i + 1).map((week) => {
                const weekDays = activePlan.days.filter((d) => d.week_number === week);
                const weekCompleted = weekDays.filter((d) => d.status === "completed").length;
                const isCurrentWeek = weekDays.some(
                  (d) => d.status === "available" || d.status === "in_progress"
                );

                return (
                  <div key={week} className="mb-6 animate-fade-in-up">
                    <div className="flex items-center gap-2 mb-3">
                      <h3 className="text-sm font-medium text-slate-500">
                        Woche {week}
                      </h3>
                      <span className="text-xs text-slate-400 stat-number">
                        {weekCompleted}/{weekDays.length} abgeschlossen
                      </span>
                      {isCurrentWeek && (
                        <span className="text-xs bg-scil/10 text-scil px-2 py-0.5 rounded-full">
                          Aktuell
                        </span>
                      )}
                    </div>
                    <div className="grid gap-3 md:grid-cols-2">
                      {weekDays.map((day, dayIndex) => (
                        <DayCard
                          key={day.id}
                          day={day}
                          isActive={day.status === "available" || day.status === "in_progress"}
                          onStart={() => handleStartDay(day.id)}
                          onComplete={() => handleOpenCompletion(day)}
                          className={`stagger-${Math.min(dayIndex + 1, 6)}`}
                        />
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* Plans List (if no active plan detail) */}
          {!activePlan && plans.length > 0 && (
            <div className="mb-8 animate-fade-in-up">
              <h2 className="text-lg font-semibold text-slate-900 mb-4">Meine Trainingsplaene</h2>
              <div className="space-y-3">
                {plans.map((plan, planIndex) => (
                  <div
                    key={plan.id}
                    onClick={() => handleViewPlan(plan.id)}
                    className={`glass-card-interactive rounded-2xl p-4 cursor-pointer transition-all stagger-${Math.min(planIndex + 1, 6)}`}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-slate-900 font-medium">{plan.title}</h3>
                        <p className="text-sm text-slate-500 mt-1">
                          {plan.total_weeks} Wochen &middot; {plan.days_per_week} Tage/Woche
                        </p>
                      </div>
                      <div className="flex items-center gap-3">
                        <span
                          className={`text-xs font-medium px-2 py-1 rounded-full ${
                            plan.status === "active"
                              ? "bg-scil/10 text-scil"
                              : plan.status === "completed"
                              ? "bg-emerald-500/10 text-emerald-400"
                              : "bg-slate-500/10 text-slate-400"
                          }`}
                        >
                          {plan.status === "active" ? "Aktiv" :
                           plan.status === "completed" ? "Abgeschlossen" :
                           plan.status === "paused" ? "Pausiert" : plan.status}
                        </span>
                        <div className="text-sm text-slate-900 font-medium stat-number">
                          {Math.round(plan.overall_progress * 100)}%
                        </div>
                      </div>
                    </div>
                    <div className="mt-3 h-1.5 bg-black/[0.02] rounded-full overflow-hidden">
                      <div
                        className="h-full bg-scil rounded-full transition-all duration-500"
                        style={{ width: `${plan.overall_progress * 100}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </AppShell>

      {/* Completion Modal */}
      {showCompletion && (
        <CompletionModal
          day={showCompletion}
          onClose={() => setShowCompletion(null)}
          onSubmit={handleCompleteDay}
          isSubmitting={submitting}
        />
      )}
    </>
  );
}
