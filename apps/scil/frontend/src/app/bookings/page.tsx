"use client";

import { useState, useEffect } from "react";
import { useBookings } from "@/hooks/useBookings";
import { useAuth } from "@/hooks/useAuth";
import type { Booking, AvailabilitySlot, SessionBriefing } from "@/lib/types";

// ── Day names ─────────────────────────────────────────────────────────
const DAY_NAMES = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"];
const DAY_SHORT = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"];

// ── Status config ─────────────────────────────────────────────────────
const STATUS_CONFIG: Record<string, { label: string; color: string; bg: string }> = {
  requested: { label: "Ausstehend", color: "text-amber-400", bg: "bg-amber-400/10" },
  confirmed: { label: "Bestaetigt", color: "text-green-400", bg: "bg-green-400/10" },
  cancelled: { label: "Abgesagt", color: "text-red-400", bg: "bg-red-400/10" },
  completed: { label: "Abgeschlossen", color: "text-blue-400", bg: "bg-blue-400/10" },
  no_show: { label: "Nicht erschienen", color: "text-slate-400", bg: "bg-slate-400/10" },
};

// ── Stat Card ─────────────────────────────────────────────────────────
function StatCard({ label, value, sub }: { label: string; value: string | number; sub?: string }) {
  return (
    <div className="bg-surface rounded-xl p-4 border border-border">
      <div className="text-xs text-slate-500 uppercase tracking-wider mb-1">{label}</div>
      <div className="text-2xl font-bold text-white">{value}</div>
      {sub && <div className="text-xs text-slate-400 mt-1">{sub}</div>}
    </div>
  );
}

// ── Booking Card ──────────────────────────────────────────────────────
function BookingCard({
  booking,
  isCoach,
  onConfirm,
  onCancel,
  onComplete,
  onViewBriefing,
}: {
  booking: Booking;
  isCoach: boolean;
  onConfirm: (id: string) => void;
  onCancel: (id: string) => void;
  onComplete: (id: string) => void;
  onViewBriefing: (id: string) => void;
}) {
  const dt = new Date(booking.scheduled_at);
  const dateStr = dt.toLocaleDateString("de-DE", {
    weekday: "short",
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
  const timeStr = dt.toLocaleTimeString("de-DE", {
    hour: "2-digit",
    minute: "2-digit",
  });
  const statusCfg = STATUS_CONFIG[booking.status] ?? STATUS_CONFIG.pending;
  const partnerName = isCoach
    ? booking.coachee_name ?? "Coachee"
    : booking.coach_name ?? "Coach";

  return (
    <div className="bg-surface rounded-xl border border-border p-5 hover:border-scil/30 transition-colors">
      <div className="flex items-start justify-between mb-3">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className={`text-xs px-2 py-0.5 rounded-full ${statusCfg.bg} ${statusCfg.color}`}>
              {statusCfg.label}
            </span>
            {booking.has_briefing && isCoach && (
              <span className="text-xs px-2 py-0.5 rounded-full bg-purple-400/10 text-purple-400">
                Briefing
              </span>
            )}
          </div>
          <h3 className="text-white font-medium">
            {booking.topic ?? "Coaching-Session"}
          </h3>
          <p className="text-sm text-slate-400">mit {partnerName}</p>
        </div>
        <div className="text-right">
          <div className="text-sm text-white font-medium">{dateStr}</div>
          <div className="text-sm text-scil">{timeStr} Uhr</div>
          <div className="text-xs text-slate-500">{booking.duration_minutes} Min.</div>
        </div>
      </div>

      {booking.coachee_notes && (
        <div className="text-xs text-slate-400 bg-surface-dark rounded-lg p-3 mb-3">
          <span className="text-slate-500">Notiz:</span> {booking.coachee_notes}
        </div>
      )}

      {booking.summary && (
        <div className="text-xs text-slate-400 bg-surface-dark rounded-lg p-3 mb-3">
          <span className="text-slate-500">Zusammenfassung:</span> {booking.summary}
        </div>
      )}

      {booking.meeting_link && booking.status === "confirmed" && (
        <a
          href={booking.meeting_link}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1 text-xs text-scil hover:text-scil-light mb-3"
        >
          Meeting-Link
        </a>
      )}

      {/* Actions */}
      <div className="flex gap-2 mt-2">
        {isCoach && booking.status === "requested" && (
          <button
            onClick={() => onConfirm(booking.id)}
            className="px-3 py-1.5 text-xs bg-green-500/10 text-green-400 hover:bg-green-500/20 rounded-lg transition-colors"
          >
            Bestaetigen
          </button>
        )}
        {booking.status === "confirmed" && isCoach && (
          <button
            onClick={() => onComplete(booking.id)}
            className="px-3 py-1.5 text-xs bg-blue-500/10 text-blue-400 hover:bg-blue-500/20 rounded-lg transition-colors"
          >
            Abschliessen
          </button>
        )}
        {(booking.status === "requested" || booking.status === "confirmed") && (
          <button
            onClick={() => onCancel(booking.id)}
            className="px-3 py-1.5 text-xs bg-red-500/10 text-red-400 hover:bg-red-500/20 rounded-lg transition-colors"
          >
            Absagen
          </button>
        )}
        {isCoach && booking.has_briefing && (
          <button
            onClick={() => onViewBriefing(booking.id)}
            className="px-3 py-1.5 text-xs bg-purple-500/10 text-purple-400 hover:bg-purple-500/20 rounded-lg transition-colors"
          >
            Briefing ansehen
          </button>
        )}
      </div>
    </div>
  );
}

// ── Slot Manager (Coach) ──────────────────────────────────────────────
function SlotManager({
  slots,
  onCreateSlot,
  onDeleteSlot,
}: {
  slots: AvailabilitySlot[];
  onCreateSlot: (slot: {
    day_of_week: number;
    start_time: string;
    end_time: string;
    duration_minutes: number;
  }) => Promise<void>;
  onDeleteSlot: (id: string) => Promise<void>;
}) {
  const [showForm, setShowForm] = useState(false);
  const [dayOfWeek, setDayOfWeek] = useState(0);
  const [startTime, setStartTime] = useState("09:00");
  const [endTime, setEndTime] = useState("12:00");
  const [duration, setDuration] = useState(60);
  const [creating, setCreating] = useState(false);

  const handleCreate = async () => {
    setCreating(true);
    try {
      await onCreateSlot({
        day_of_week: dayOfWeek,
        start_time: startTime,
        end_time: endTime,
        duration_minutes: duration,
      });
      setShowForm(false);
    } finally {
      setCreating(false);
    }
  };

  // Group slots by day
  const slotsByDay: Record<number, AvailabilitySlot[]> = {};
  slots.forEach((s) => {
    if (!slotsByDay[s.day_of_week]) slotsByDay[s.day_of_week] = [];
    slotsByDay[s.day_of_week].push(s);
  });

  return (
    <div className="bg-surface rounded-xl border border-border p-5">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-white">Verfuegbarkeit</h2>
        <button
          onClick={() => setShowForm(!showForm)}
          className="px-3 py-1.5 text-sm bg-scil hover:bg-scil-dark text-white rounded-lg transition-colors"
        >
          {showForm ? "Abbrechen" : "+ Slot hinzufuegen"}
        </button>
      </div>

      {showForm && (
        <div className="bg-surface-dark rounded-lg p-4 mb-4 space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs text-slate-400 mb-1">Tag</label>
              <select
                value={dayOfWeek}
                onChange={(e) => setDayOfWeek(Number(e.target.value))}
                className="w-full bg-surface border border-border rounded-lg px-3 py-2 text-sm text-white"
              >
                {DAY_NAMES.map((name, i) => (
                  <option key={i} value={i}>
                    {name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs text-slate-400 mb-1">
                Dauer (Min.)
              </label>
              <select
                value={duration}
                onChange={(e) => setDuration(Number(e.target.value))}
                className="w-full bg-surface border border-border rounded-lg px-3 py-2 text-sm text-white"
              >
                <option value={30}>30</option>
                <option value={45}>45</option>
                <option value={60}>60</option>
                <option value={90}>90</option>
              </select>
            </div>
            <div>
              <label className="block text-xs text-slate-400 mb-1">Von</label>
              <input
                type="time"
                value={startTime}
                onChange={(e) => setStartTime(e.target.value)}
                className="w-full bg-surface border border-border rounded-lg px-3 py-2 text-sm text-white"
              />
            </div>
            <div>
              <label className="block text-xs text-slate-400 mb-1">Bis</label>
              <input
                type="time"
                value={endTime}
                onChange={(e) => setEndTime(e.target.value)}
                className="w-full bg-surface border border-border rounded-lg px-3 py-2 text-sm text-white"
              />
            </div>
          </div>
          <button
            onClick={handleCreate}
            disabled={creating}
            className="w-full py-2 bg-scil hover:bg-scil-dark text-white rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
          >
            {creating ? "Erstelle..." : "Slot erstellen"}
          </button>
        </div>
      )}

      {/* Week overview */}
      <div className="grid grid-cols-7 gap-1">
        {DAY_SHORT.map((day, i) => (
          <div key={i} className="text-center">
            <div className="text-xs text-slate-500 font-medium mb-2">{day}</div>
            <div className="space-y-1 min-h-[60px]">
              {(slotsByDay[i] ?? []).map((slot) => (
                <div
                  key={slot.id}
                  className="group relative bg-scil/10 border border-scil/20 rounded-md px-1 py-1 text-center"
                >
                  <div className="text-[10px] text-scil leading-tight">
                    {slot.start_time}
                  </div>
                  <div className="text-[10px] text-scil leading-tight">
                    {slot.end_time}
                  </div>
                  <button
                    onClick={() => onDeleteSlot(slot.id)}
                    className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 text-white rounded-full text-[8px] leading-none opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center"
                    title="Loeschen"
                  >
                    x
                  </button>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {slots.length === 0 && (
        <div className="text-center text-slate-500 text-sm py-6">
          Noch keine Verfuegbarkeits-Slots angelegt.
        </div>
      )}
    </div>
  );
}

// ── Briefing Panel ────────────────────────────────────────────────────
function BriefingPanel({
  briefing,
  onClose,
  onRegenerate,
}: {
  briefing: SessionBriefing;
  onClose: () => void;
  onRegenerate: () => void;
}) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="bg-surface-dark border border-border rounded-2xl max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-white">Session Briefing</h2>
            <button
              onClick={onClose}
              className="text-slate-400 hover:text-white text-xl"
            >
              x
            </button>
          </div>

          {briefing.status === "generating" ? (
            <div className="text-center py-8">
              <div className="animate-spin w-8 h-8 border-2 border-scil border-t-transparent rounded-full mx-auto mb-3" />
              <p className="text-slate-400">Briefing wird generiert...</p>
            </div>
          ) : (
            <div className="space-y-4">
              {briefing.coachee_profile_summary && (
                <div>
                  <h3 className="text-sm font-medium text-slate-300 mb-1">Coachee-Profil</h3>
                  <p className="text-sm text-slate-400 bg-surface rounded-lg p-3">
                    {briefing.coachee_profile_summary}
                  </p>
                </div>
              )}

              {briefing.scil_highlights && (
                <div>
                  <h3 className="text-sm font-medium text-slate-300 mb-1">SCIL Highlights</h3>
                  <div className="bg-surface rounded-lg p-3">
                    {Object.entries(briefing.scil_highlights).map(([key, val]) => (
                      <div key={key} className="flex justify-between text-sm py-0.5">
                        <span className="text-slate-400 capitalize">{key}</span>
                        <span className="text-white">{String(val)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {briefing.suggested_topics && briefing.suggested_topics.length > 0 && (
                <div>
                  <h3 className="text-sm font-medium text-slate-300 mb-1">
                    Vorgeschlagene Themen
                  </h3>
                  <ul className="space-y-1">
                    {briefing.suggested_topics.map((topic, i) => (
                      <li
                        key={i}
                        className="text-sm text-slate-400 bg-surface rounded-lg px-3 py-2"
                      >
                        {topic}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {briefing.suggested_exercises && briefing.suggested_exercises.length > 0 && (
                <div>
                  <h3 className="text-sm font-medium text-slate-300 mb-1">
                    Vorgeschlagene Uebungen
                  </h3>
                  <ul className="space-y-1">
                    {briefing.suggested_exercises.map((ex, i) => (
                      <li
                        key={i}
                        className="text-sm text-slate-400 bg-surface rounded-lg px-3 py-2"
                      >
                        {ex}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {briefing.previous_session_notes && (
                <div>
                  <h3 className="text-sm font-medium text-slate-300 mb-1">
                    Vorherige Sessions
                  </h3>
                  <p className="text-sm text-slate-400 bg-surface rounded-lg p-3">
                    {briefing.previous_session_notes}
                  </p>
                </div>
              )}

              {briefing.training_progress_summary && (
                <div>
                  <h3 className="text-sm font-medium text-slate-300 mb-1">
                    Trainingsfortschritt
                  </h3>
                  <p className="text-sm text-slate-400 bg-surface rounded-lg p-3">
                    {briefing.training_progress_summary}
                  </p>
                </div>
              )}

              {briefing.content && (
                <div>
                  <h3 className="text-sm font-medium text-slate-300 mb-1">
                    Briefing
                  </h3>
                  <div className="text-sm text-slate-400 bg-surface rounded-lg p-3 whitespace-pre-wrap">
                    {briefing.content}
                  </div>
                </div>
              )}
            </div>
          )}

          <div className="flex gap-2 mt-6">
            <button
              onClick={onRegenerate}
              className="px-4 py-2 text-sm bg-purple-500/10 text-purple-400 hover:bg-purple-500/20 rounded-lg transition-colors"
            >
              Neu generieren
            </button>
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm bg-surface text-slate-300 hover:bg-surface-hover rounded-lg transition-colors"
            >
              Schliessen
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// ── New Booking Modal ─────────────────────────────────────────────────
function NewBookingModal({
  coachId,
  onClose,
  onBook,
}: {
  coachId: string;
  onClose: () => void;
  onBook: (data: {
    coach_id: string;
    scheduled_at: string;
    topic?: string;
    coachee_notes?: string;
    slot_id?: string;
  }) => Promise<void>;
}) {
  const [date, setDate] = useState("");
  const [time, setTime] = useState("09:00");
  const [topic, setTopic] = useState("");
  const [notes, setNotes] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async () => {
    if (!date || !time) return;
    setSubmitting(true);
    try {
      const scheduled = `${date}T${time}:00`;
      await onBook({
        coach_id: coachId,
        scheduled_at: scheduled,
        topic: topic || undefined,
        coachee_notes: notes || undefined,
      });
      onClose();
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="bg-surface-dark border border-border rounded-2xl max-w-md w-full mx-4 p-6">
        <h2 className="text-lg font-semibold text-white mb-4">Neue Buchung</h2>

        <div className="space-y-3">
          <div>
            <label className="block text-xs text-slate-400 mb-1">Datum</label>
            <input
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              className="w-full bg-surface border border-border rounded-lg px-3 py-2 text-sm text-white"
            />
          </div>
          <div>
            <label className="block text-xs text-slate-400 mb-1">Uhrzeit</label>
            <input
              type="time"
              value={time}
              onChange={(e) => setTime(e.target.value)}
              className="w-full bg-surface border border-border rounded-lg px-3 py-2 text-sm text-white"
            />
          </div>
          <div>
            <label className="block text-xs text-slate-400 mb-1">Thema (optional)</label>
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="z.B. Kommunikation verbessern"
              className="w-full bg-surface border border-border rounded-lg px-3 py-2 text-sm text-white placeholder:text-slate-600"
            />
          </div>
          <div>
            <label className="block text-xs text-slate-400 mb-1">Notizen (optional)</label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={3}
              placeholder="Was moechtest du besprechen?"
              className="w-full bg-surface border border-border rounded-lg px-3 py-2 text-sm text-white placeholder:text-slate-600 resize-none"
            />
          </div>
        </div>

        <div className="flex gap-2 mt-5">
          <button
            onClick={handleSubmit}
            disabled={!date || submitting}
            className="flex-1 py-2 bg-scil hover:bg-scil-dark text-white rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
          >
            {submitting ? "Buche..." : "Buchen"}
          </button>
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm bg-surface text-slate-300 hover:bg-surface-hover rounded-lg transition-colors"
          >
            Abbrechen
          </button>
        </div>
      </div>
    </div>
  );
}

// ── Complete Booking Modal ────────────────────────────────────────────
function CompleteModal({
  onClose,
  onComplete,
}: {
  onClose: () => void;
  onComplete: (notes: string, summary: string) => Promise<void>;
}) {
  const [coachNotes, setCoachNotes] = useState("");
  const [summary, setSummary] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      await onComplete(coachNotes, summary);
      onClose();
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="bg-surface-dark border border-border rounded-2xl max-w-md w-full mx-4 p-6">
        <h2 className="text-lg font-semibold text-white mb-4">Session abschliessen</h2>

        <div className="space-y-3">
          <div>
            <label className="block text-xs text-slate-400 mb-1">Coach-Notizen</label>
            <textarea
              value={coachNotes}
              onChange={(e) => setCoachNotes(e.target.value)}
              rows={3}
              placeholder="Interne Notizen zur Session..."
              className="w-full bg-surface border border-border rounded-lg px-3 py-2 text-sm text-white placeholder:text-slate-600 resize-none"
            />
          </div>
          <div>
            <label className="block text-xs text-slate-400 mb-1">Zusammenfassung</label>
            <textarea
              value={summary}
              onChange={(e) => setSummary(e.target.value)}
              rows={3}
              placeholder="Oeffentliche Zusammenfassung der Session..."
              className="w-full bg-surface border border-border rounded-lg px-3 py-2 text-sm text-white placeholder:text-slate-600 resize-none"
            />
          </div>
        </div>

        <div className="flex gap-2 mt-5">
          <button
            onClick={handleSubmit}
            disabled={submitting}
            className="flex-1 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
          >
            {submitting ? "Speichere..." : "Abschliessen"}
          </button>
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm bg-surface text-slate-300 hover:bg-surface-hover rounded-lg transition-colors"
          >
            Abbrechen
          </button>
        </div>
      </div>
    </div>
  );
}

// ══════════════════════════════════════════════════════════════════════
// Main Page
// ══════════════════════════════════════════════════════════════════════
export default function BookingsPage() {
  const { user, isAuthenticated, isLoading: authLoading } = useAuth();
  const {
    slots,
    bookings,
    upcomingBookings,
    currentBriefing,
    isLoading,
    error,
    clearError,
    fetchSlots,
    createSlot,
    deleteSlot,
    fetchBookings,
    fetchUpcoming,
    confirmBooking,
    cancelBooking,
    completeBooking,
    createBooking,
    fetchBriefing,
    regenerateBriefing,
  } = useBookings();

  const [activeTab, setActiveTab] = useState<"upcoming" | "all" | "slots">("upcoming");
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [showNewBooking, setShowNewBooking] = useState(false);
  const [showBriefing, setShowBriefing] = useState(false);
  const [showComplete, setShowComplete] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState(false);

  const isCoach = user?.role === "coach" || user?.role === "admin";

  // Redirect if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      window.location.href = "/";
    }
  }, [authLoading, isAuthenticated]);

  // Refresh bookings when filter changes
  useEffect(() => {
    if (activeTab === "all") {
      fetchBookings(isCoach ? "coach" : undefined, statusFilter || undefined);
    }
  }, [activeTab, statusFilter, isCoach, fetchBookings]);

  if (authLoading || !isAuthenticated) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="animate-spin w-8 h-8 border-2 border-scil border-t-transparent rounded-full" />
      </div>
    );
  }

  // Stats
  const pendingCount = bookings.filter((b) => b.status === "requested").length;
  const confirmedCount = bookings.filter((b) => b.status === "confirmed").length;
  const completedCount = bookings.filter((b) => b.status === "completed").length;

  const handleConfirm = async (id: string) => {
    setActionLoading(true);
    try {
      await confirmBooking(id);
      fetchUpcoming();
    } catch (e) {
      console.error(e);
    } finally {
      setActionLoading(false);
    }
  };

  const handleCancel = async (id: string) => {
    setActionLoading(true);
    try {
      await cancelBooking(id);
      fetchUpcoming();
    } catch (e) {
      console.error(e);
    } finally {
      setActionLoading(false);
    }
  };

  const handleComplete = async (id: string) => {
    setShowComplete(id);
  };

  const handleCompleteSubmit = async (notes: string, summary: string) => {
    if (!showComplete) return;
    setActionLoading(true);
    try {
      await completeBooking(showComplete, {
        coach_notes: notes || undefined,
        summary: summary || undefined,
      });
      fetchUpcoming();
      setShowComplete(null);
    } catch (e) {
      console.error(e);
    } finally {
      setActionLoading(false);
    }
  };

  const handleViewBriefing = async (bookingId: string) => {
    try {
      await fetchBriefing(bookingId);
      setShowBriefing(true);
    } catch (e) {
      console.error(e);
    }
  };

  const handleCreateBooking = async (data: {
    coach_id: string;
    scheduled_at: string;
    topic?: string;
    coachee_notes?: string;
    slot_id?: string;
  }) => {
    await createBooking(data);
    fetchUpcoming();
    fetchBookings();
  };

  const handleCreateSlot = async (slot: {
    day_of_week: number;
    start_time: string;
    end_time: string;
    duration_minutes: number;
  }) => {
    await createSlot(slot);
  };

  const handleDeleteSlot = async (id: string) => {
    await deleteSlot(id);
  };

  const handleRegenerate = async () => {
    // Find the booking ID from the current briefing context
    // The briefing panel is shown for a specific booking
    if (currentBriefing) {
      const bookingId = bookings.find((b) => b.has_briefing)?.id;
      if (bookingId) {
        await regenerateBriefing(bookingId);
      }
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-surface-dark">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <a href="/dashboard" className="text-slate-400 hover:text-white text-sm">
              Dashboard
            </a>
            <span className="text-slate-600">/</span>
            <h1 className="text-lg font-semibold text-white">Buchungen</h1>
          </div>
          {!isCoach && (
            <button
              onClick={() => setShowNewBooking(true)}
              className="px-4 py-2 bg-scil hover:bg-scil-dark text-white rounded-lg text-sm font-medium transition-colors"
            >
              + Neue Buchung
            </button>
          )}
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-6 space-y-6">
        {/* Error banner */}
        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 flex items-center justify-between">
            <span className="text-sm text-red-400">{error}</span>
            <button onClick={clearError} className="text-red-400 hover:text-red-300 text-sm">
              x
            </button>
          </div>
        )}

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard label="Ausstehend" value={pendingCount} />
          <StatCard label="Bestaetigt" value={confirmedCount} />
          <StatCard label="Abgeschlossen" value={completedCount} />
          <StatCard
            label={isCoach ? "Slots" : "Naechste Session"}
            value={
              isCoach
                ? slots.length
                : upcomingBookings.length > 0
                ? new Date(upcomingBookings[0].scheduled_at).toLocaleDateString(
                    "de-DE",
                    { day: "2-digit", month: "2-digit" }
                  )
                : "--"
            }
          />
        </div>

        {/* Tabs */}
        <div className="flex gap-1 bg-surface-dark rounded-lg p-1 border border-border">
          <button
            onClick={() => setActiveTab("upcoming")}
            className={`flex-1 px-4 py-2 text-sm rounded-md transition-colors ${
              activeTab === "upcoming"
                ? "bg-scil text-white"
                : "text-slate-400 hover:text-white"
            }`}
          >
            Naechste Sessions
          </button>
          <button
            onClick={() => setActiveTab("all")}
            className={`flex-1 px-4 py-2 text-sm rounded-md transition-colors ${
              activeTab === "all"
                ? "bg-scil text-white"
                : "text-slate-400 hover:text-white"
            }`}
          >
            Alle Buchungen
          </button>
          {isCoach && (
            <button
              onClick={() => setActiveTab("slots")}
              className={`flex-1 px-4 py-2 text-sm rounded-md transition-colors ${
                activeTab === "slots"
                  ? "bg-scil text-white"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              Verfuegbarkeit
            </button>
          )}
        </div>

        {/* Tab content */}
        {activeTab === "upcoming" && (
          <div className="space-y-4">
            {isLoading ? (
              <div className="text-center py-12">
                <div className="animate-spin w-8 h-8 border-2 border-scil border-t-transparent rounded-full mx-auto" />
              </div>
            ) : upcomingBookings.length === 0 ? (
              <div className="text-center py-12 bg-surface rounded-xl border border-border">
                <div className="text-4xl mb-3">
                  {isCoach ? "📅" : "🎯"}
                </div>
                <p className="text-slate-400 mb-2">Keine kommenden Sessions</p>
                {!isCoach && (
                  <button
                    onClick={() => setShowNewBooking(true)}
                    className="text-sm text-scil hover:text-scil-light"
                  >
                    Jetzt eine Session buchen
                  </button>
                )}
              </div>
            ) : (
              upcomingBookings.map((b) => (
                <BookingCard
                  key={b.id}
                  booking={b}
                  isCoach={isCoach}
                  onConfirm={handleConfirm}
                  onCancel={handleCancel}
                  onComplete={handleComplete}
                  onViewBriefing={handleViewBriefing}
                />
              ))
            )}
          </div>
        )}

        {activeTab === "all" && (
          <div className="space-y-4">
            {/* Status filter */}
            <div className="flex gap-2">
              {["", "requested", "confirmed", "completed", "cancelled"].map(
                (st) => (
                  <button
                    key={st}
                    onClick={() => setStatusFilter(st)}
                    className={`px-3 py-1 text-xs rounded-full transition-colors ${
                      statusFilter === st
                        ? "bg-scil text-white"
                        : "bg-surface text-slate-400 hover:text-white"
                    }`}
                  >
                    {st === ""
                      ? "Alle"
                      : STATUS_CONFIG[st]?.label ?? st}
                  </button>
                )
              )}
            </div>

            {isLoading ? (
              <div className="text-center py-12">
                <div className="animate-spin w-8 h-8 border-2 border-scil border-t-transparent rounded-full mx-auto" />
              </div>
            ) : bookings.length === 0 ? (
              <div className="text-center py-12 bg-surface rounded-xl border border-border">
                <p className="text-slate-400">Keine Buchungen gefunden</p>
              </div>
            ) : (
              bookings.map((b) => (
                <BookingCard
                  key={b.id}
                  booking={b}
                  isCoach={isCoach}
                  onConfirm={handleConfirm}
                  onCancel={handleCancel}
                  onComplete={handleComplete}
                  onViewBriefing={handleViewBriefing}
                />
              ))
            )}
          </div>
        )}

        {activeTab === "slots" && isCoach && (
          <SlotManager
            slots={slots}
            onCreateSlot={handleCreateSlot}
            onDeleteSlot={handleDeleteSlot}
          />
        )}
      </main>

      {/* Modals */}
      {showNewBooking && (
        <NewBookingModal
          coachId=""
          onClose={() => setShowNewBooking(false)}
          onBook={handleCreateBooking}
        />
      )}

      {showBriefing && currentBriefing && (
        <BriefingPanel
          briefing={currentBriefing}
          onClose={() => setShowBriefing(false)}
          onRegenerate={handleRegenerate}
        />
      )}

      {showComplete && (
        <CompleteModal
          onClose={() => setShowComplete(null)}
          onComplete={handleCompleteSubmit}
        />
      )}

      {/* Loading overlay for actions */}
      {actionLoading && (
        <div className="fixed inset-0 z-40 bg-black/20 flex items-center justify-center">
          <div className="animate-spin w-8 h-8 border-2 border-scil border-t-transparent rounded-full" />
        </div>
      )}
    </div>
  );
}
