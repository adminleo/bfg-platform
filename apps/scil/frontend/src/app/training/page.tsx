"use client";

import { useState, useEffect, useMemo } from "react";
import { useRouter } from "next/navigation";
import { useDailyTraining } from "@/hooks/useDailyTraining";
import { api } from "@/lib/api";
import { AppShell } from "@/components/layout/AppShell";
import { TrainingSidebar } from "@/components/training/TrainingSidebar";
import type { TrainingDay, TrainingContentItem } from "@/lib/types";

// Enrollment state type
interface EnrollmentInfo {
  content_id: string;
  status: string;
  enrolled_at: string;
  completed_at: string | null;
}

// ---------------------------------------------------------------------------
// Area config
// ---------------------------------------------------------------------------
const AREA_CONFIG: Record<string, { label: string; color: string; icon: string }> = {
  sensus: { label: "Sensus", color: "text-rose-600", icon: "S" },
  corpus: { label: "Corpus", color: "text-amber-600", icon: "C" },
  intellektus: { label: "Intellektus", color: "text-blue-600", icon: "I" },
  lingua: { label: "Lingua", color: "text-emerald-600", icon: "L" },
  general: { label: "Allgemein", color: "text-slate-500", icon: "G" },
};

const AREA_BG: Record<string, string> = {
  sensus: "bg-rose-500/20",
  corpus: "bg-amber-500/20",
  intellektus: "bg-blue-500/20",
  lingua: "bg-emerald-500/20",
  general: "bg-slate-500/20",
};

const AREA_BORDER: Record<string, string> = {
  sensus: "border-rose-500/30",
  corpus: "border-amber-500/30",
  intellektus: "border-blue-500/30",
  lingua: "border-emerald-500/30",
  general: "border-slate-500/30",
};

const CONTENT_TYPE_LABELS: Record<string, string> = {
  exercise: "Uebung",
  reflection: "Reflexion",
  article: "Artikel",
  video: "Video",
  quiz: "Quiz",
};

const CONTENT_TYPE_ICONS: Record<string, React.ReactNode> = {
  video: (
    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  ),
  exercise: (
    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 4a2 2 0 114 0v1a1 1 0 001 1h3a1 1 0 011 1v3a1 1 0 01-1 1h-1a2 2 0 100 4h1a1 1 0 011 1v3a1 1 0 01-1 1h-3a1 1 0 01-1-1v-1a2 2 0 10-4 0v1a1 1 0 01-1 1H7a1 1 0 01-1-1v-3a1 1 0 00-1-1H4a2 2 0 110-4h1a1 1 0 001-1V7a1 1 0 011-1h3a1 1 0 001-1V4z" />
    </svg>
  ),
  reflection: (
    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
    </svg>
  ),
  article: (
    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
    </svg>
  ),
  quiz: (
    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  ),
};

const AREA_FILTERS = [
  { key: "all", label: "Alle" },
  { key: "sensus", label: "Sensus" },
  { key: "corpus", label: "Corpus" },
  { key: "intellektus", label: "Intellektus" },
  { key: "lingua", label: "Lingua" },
  { key: "general", label: "Allgemein" },
] as const;

// ---------------------------------------------------------------------------
// Difficulty dots
// ---------------------------------------------------------------------------
function DifficultyDots({ level, max = 5 }: { level: number; max?: number }) {
  return (
    <div className="flex gap-0.5">
      {Array.from({ length: max }, (_, i) => (
        <div
          key={i}
          className={`w-1.5 h-1.5 rounded-full ${
            i < level ? "bg-slate-900" : "bg-black/[0.08]"
          }`}
        />
      ))}
    </div>
  );
}

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
  const router = useRouter();
  const area = AREA_CONFIG[day.area] || AREA_CONFIG.general;
  const areaBg = AREA_BG[day.area] || AREA_BG.general;
  const isLocked = day.status === "locked";
  const isCompleted = day.status === "completed";
  const isAvailable = day.status === "available";
  const isInProgress = day.status === "in_progress";

  const handleCardClick = () => {
    if (!isLocked && day.content?.id) {
      router.push(`/training/${day.content.id}`);
    }
  };

  return (
    <div
      onClick={handleCardClick}
      className={`glass-card-interactive p-4 rounded-2xl transition-all ${
        !isLocked && day.content?.id ? "cursor-pointer" : ""
      } ${
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
            <div className="text-xs text-slate-500">
              Woche {day.week_number}, Tag {day.day_number}
              {day.content && ` \u00B7 ${day.content.duration_minutes} Min.`}
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {day.content && !isLocked && (
            <span className={`inline-flex items-center gap-1 text-[10px] px-2 py-0.5 rounded-full ${areaBg} ${area.color}`}>
              {CONTENT_TYPE_ICONS[day.content.content_type]}
              {CONTENT_TYPE_LABELS[day.content.content_type] || day.content.content_type}
            </span>
          )}
          {isCompleted && (
            <span className="text-xs font-medium text-emerald-600 bg-emerald-500/10 px-2 py-1 rounded-full">
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

      {/* Author */}
      {day.content?.author && !isLocked && (
        <div className="flex items-center gap-1.5 mb-2">
          <div className="w-4 h-4 rounded-full bg-black/[0.06] flex items-center justify-center">
            <svg className="w-2.5 h-2.5 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </div>
          <span className="text-[11px] text-slate-500">{day.content.author}</span>
        </div>
      )}

      {day.coaching_note && !isLocked && (
        <p className="text-xs text-slate-500 mb-3 italic">
          {day.coaching_note}
        </p>
      )}

      {day.content && !isLocked && (
        <div className="mb-3">
          <p className="text-xs text-slate-500 mt-1 line-clamp-2">{day.content.description}</p>
        </div>
      )}

      <div className="flex gap-2" onClick={(e) => e.stopPropagation()}>
        {isAvailable && (
          <button
            onClick={onStart}
            className="flex-1 py-2 btn-glass text-white text-sm font-medium rounded-xl transition-colors"
          >
            Training starten
          </button>
        )}
        {isInProgress && (
          <button
            onClick={onComplete}
            className="flex-1 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-medium rounded-xl transition-colors"
          >
            Als fertig markieren
          </button>
        )}
      </div>

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
// Content Library Card
// ---------------------------------------------------------------------------
function ContentCard({ item, enrollmentStatus }: { item: TrainingContentItem; enrollmentStatus?: string }) {
  const router = useRouter();
  const area = AREA_CONFIG[item.area] || AREA_CONFIG.general;
  const areaBg = AREA_BG[item.area] || AREA_BG.general;
  const areaBorder = AREA_BORDER[item.area] || AREA_BORDER.general;

  return (
    <div
      onClick={() => router.push(`/training/${item.id}`)}
      className="glass-card-interactive p-5 rounded-2xl cursor-pointer transition-all hover:scale-[1.01] flex flex-col"
    >
      {/* Top row: area indicator + type badge */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className={`w-7 h-7 rounded-lg ${areaBg} flex items-center justify-center ${area.color} font-bold text-xs`}>
            {area.icon}
          </div>
          <span className={`inline-flex items-center gap-1 text-[10px] font-medium px-2 py-0.5 rounded-full ${areaBg} ${area.color}`}>
            {CONTENT_TYPE_ICONS[item.content_type]}
            {CONTENT_TYPE_LABELS[item.content_type] || item.content_type}
          </span>
        </div>
        <div className="flex items-center gap-1.5">
          {/* Enrollment badge */}
          {enrollmentStatus === "completed" ? (
            <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-600 border border-emerald-500/20 flex items-center gap-1">
              <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              Abgeschlossen
            </span>
          ) : enrollmentStatus === "active" ? (
            <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-scil/15 text-scil border border-scil/20">
              Eingeschrieben
            </span>
          ) : null}
          {/* Premium / Free badge */}
          {item.is_premium ? (
            <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-amber-500/15 text-amber-600 border border-amber-500/20">
              Premium
            </span>
          ) : (
            <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-600 border border-emerald-500/20">
              Kostenlos
            </span>
          )}
        </div>
      </div>

      {/* Title */}
      <h3 className="text-sm font-semibold text-slate-900 mb-1 line-clamp-2">{item.title}</h3>

      {/* Description */}
      <p className="text-xs text-slate-500 mb-3 line-clamp-2 flex-1">{item.description}</p>

      {/* Author */}
      {item.author && (
        <div className="flex items-center gap-1.5 mb-3">
          <div className="w-5 h-5 rounded-full bg-black/[0.06] flex items-center justify-center flex-shrink-0">
            <svg className="w-3 h-3 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </div>
          <span className="text-[11px] text-slate-500 truncate">{item.author}</span>
        </div>
      )}

      {/* Footer: duration, difficulty, price */}
      <div className={`flex items-center justify-between pt-3 border-t ${areaBorder}`}>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1 text-xs text-slate-500">
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {item.duration_minutes} Min.
          </div>
          <DifficultyDots level={item.difficulty} />
        </div>
        {item.is_premium && item.price_cents != null && (
          <span className="text-xs font-semibold text-slate-900 stat-number">
            {(item.price_cents / 100).toFixed(2)} EUR
          </span>
        )}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main Page
// ---------------------------------------------------------------------------

type MainTab = "plan" | "library";

export default function TrainingPage() {
  const router = useRouter();
  const {
    today,
    plans,
    activePlan,
    stats,
    contentLibrary,
    isLoading,
    error,
    generatePlan,
    startDay,
    completeDay,
    fetchPlanDetail,
    fetchContent,
  } = useDailyTraining();

  const [showCompletion, setShowCompletion] = useState<TrainingDay | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [activeTab, setActiveTab] = useState<MainTab>("plan");
  const [areaFilter, setAreaFilter] = useState<string>("all");
  const [selectedWeek, setSelectedWeek] = useState<number>(1);
  const [contentLoaded, setContentLoaded] = useState(false);
  const [enrollmentMap, setEnrollmentMap] = useState<Record<string, string>>({});

  // Determine the current week from the active plan
  useEffect(() => {
    if (activePlan) {
      // Find the current week (the one that has available or in_progress days)
      const currentWeek = activePlan.days.find(
        (d) => d.status === "available" || d.status === "in_progress"
      )?.week_number;
      if (currentWeek) {
        setSelectedWeek(currentWeek);
      }
    }
  }, [activePlan]);

  // Load content library when switching to library tab
  useEffect(() => {
    if (activeTab === "library" && !contentLoaded) {
      fetchContent().then(() => setContentLoaded(true));
    }
  }, [activeTab, contentLoaded, fetchContent]);

  // Fetch enrollment status for library tab
  useEffect(() => {
    if (activeTab === "library") {
      api
        .get<EnrollmentInfo[]>("/training/enrollments")
        .then((data) => {
          const map: Record<string, string> = {};
          for (const e of data) {
            map[e.content_id] = e.status;
          }
          setEnrollmentMap(map);
        })
        .catch(() => {});
    }
  }, [activeTab]);

  // Refetch content when area filter changes
  useEffect(() => {
    if (activeTab === "library") {
      fetchContent(areaFilter === "all" ? undefined : areaFilter);
    }
  }, [areaFilter, activeTab, fetchContent]);

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
    setActiveTab("plan");
  };

  const hasActivePlan = today?.has_training || plans.some((p) => p.status === "active");

  // Week data for the selected week
  const weekDays = useMemo(() => {
    if (!activePlan) return [];
    return activePlan.days.filter((d) => d.week_number === selectedWeek);
  }, [activePlan, selectedWeek]);

  const weekCompleted = weekDays.filter((d) => d.status === "completed").length;
  const isCurrentWeek = weekDays.some(
    (d) => d.status === "available" || d.status === "in_progress"
  );

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
            <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-600 text-sm animate-fade-in-up">
              {error}
            </div>
          )}

          {/* Page Header + Tab Navigation */}
          {!isLoading && (
            <div className="mb-6 animate-fade-in-up">
              <h1 className="text-xl font-bold text-slate-900 mb-4">Training</h1>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setActiveTab("plan")}
                  className={`px-4 py-2 text-sm font-medium rounded-full transition-all ${
                    activeTab === "plan"
                      ? "bg-scil text-white"
                      : "bg-black/[0.02] text-slate-500 border border-black/[0.06] hover:bg-black/[0.04]"
                  }`}
                >
                  Mein Plan
                </button>
                <button
                  onClick={() => setActiveTab("library")}
                  className={`px-4 py-2 text-sm font-medium rounded-full transition-all ${
                    activeTab === "library"
                      ? "bg-scil text-white"
                      : "bg-black/[0.02] text-slate-500 border border-black/[0.06] hover:bg-black/[0.04]"
                  }`}
                >
                  Alle Trainings
                </button>
              </div>
            </div>
          )}

          {/* ================================================================ */}
          {/* TAB: Mein Plan                                                   */}
          {/* ================================================================ */}
          {activeTab === "plan" && (
            <>
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

              {/* Active Plan with week navigation */}
              {activePlan && (
                <div className="mb-8 animate-fade-in-up">
                  {/* Plan header */}
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

                  {/* Week navigation bar */}
                  <div className="flex items-center justify-between mb-4 glass-card rounded-xl p-3">
                    <button
                      onClick={() => setSelectedWeek((w) => Math.max(1, w - 1))}
                      disabled={selectedWeek <= 1}
                      className="p-1.5 rounded-lg hover:bg-black/[0.04] disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                      aria-label="Vorherige Woche"
                    >
                      <svg className="w-5 h-5 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                      </svg>
                    </button>

                    <div className="flex items-center gap-3">
                      <h3 className="text-sm font-semibold text-slate-900">
                        Woche {selectedWeek}
                      </h3>
                      <span className="text-xs text-slate-500 stat-number">
                        {weekCompleted}/{weekDays.length} abgeschlossen
                      </span>
                      {isCurrentWeek && (
                        <span className="text-xs bg-scil/10 text-scil px-2 py-0.5 rounded-full font-medium">
                          Aktuell
                        </span>
                      )}
                    </div>

                    <button
                      onClick={() => setSelectedWeek((w) => Math.min(activePlan.total_weeks, w + 1))}
                      disabled={selectedWeek >= activePlan.total_weeks}
                      className="p-1.5 rounded-lg hover:bg-black/[0.04] disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                      aria-label="Naechste Woche"
                    >
                      <svg className="w-5 h-5 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </button>
                  </div>

                  {/* Week dots indicator */}
                  <div className="flex items-center justify-center gap-1.5 mb-5">
                    {Array.from({ length: activePlan.total_weeks }, (_, i) => i + 1).map((week) => {
                      const wDays = activePlan.days.filter((d) => d.week_number === week);
                      const wDone = wDays.filter((d) => d.status === "completed").length;
                      const allDone = wDone === wDays.length && wDays.length > 0;
                      const isCurrent = wDays.some(
                        (d) => d.status === "available" || d.status === "in_progress"
                      );
                      return (
                        <button
                          key={week}
                          onClick={() => setSelectedWeek(week)}
                          className={`w-2.5 h-2.5 rounded-full transition-all ${
                            week === selectedWeek
                              ? "bg-scil scale-125"
                              : allDone
                              ? "bg-emerald-400"
                              : isCurrent
                              ? "bg-scil/40"
                              : "bg-black/[0.08]"
                          }`}
                          aria-label={`Woche ${week}`}
                        />
                      );
                    })}
                  </div>

                  {/* Days for selected week */}
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
                                  ? "bg-emerald-500/10 text-emerald-600"
                                  : "bg-slate-500/10 text-slate-500"
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
            </>
          )}

          {/* ================================================================ */}
          {/* TAB: Alle Trainings (Content Library)                            */}
          {/* ================================================================ */}
          {activeTab === "library" && (
            <div className="animate-fade-in-up">
              {/* Area filter chips */}
              <div className="flex flex-wrap items-center gap-2 mb-6">
                {AREA_FILTERS.map((filter) => {
                  const isActive = areaFilter === filter.key;
                  const filterArea = AREA_CONFIG[filter.key];
                  const filterBg = AREA_BG[filter.key];
                  return (
                    <button
                      key={filter.key}
                      onClick={() => setAreaFilter(filter.key)}
                      className={`px-3.5 py-1.5 text-xs font-medium rounded-full transition-all ${
                        isActive
                          ? filter.key === "all"
                            ? "bg-scil text-white"
                            : `${filterBg} ${filterArea?.color || "text-slate-500"} ring-1 ring-current/20`
                          : "bg-black/[0.02] text-slate-500 border border-black/[0.06] hover:bg-black/[0.04]"
                      }`}
                    >
                      {filter.label}
                    </button>
                  );
                })}
              </div>

              {/* Content grid */}
              {contentLibrary.length === 0 ? (
                <div className="glass-card rounded-2xl p-8 text-center">
                  <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-black/[0.04] flex items-center justify-center">
                    <svg className="w-6 h-6 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                    </svg>
                  </div>
                  <p className="text-sm text-slate-500">
                    Keine Trainings in dieser Kategorie verfuegbar.
                  </p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {contentLibrary.map((item, index) => (
                    <div
                      key={item.id}
                      className={`stagger-${Math.min(index + 1, 6)} animate-fade-in-up`}
                    >
                      <ContentCard item={item} enrollmentStatus={enrollmentMap[item.id]} />
                    </div>
                  ))}
                </div>
              )}
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
