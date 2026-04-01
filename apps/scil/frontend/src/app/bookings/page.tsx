"use client";

import { useState, useEffect } from "react";
import { useBookings } from "@/hooks/useBookings";
import { useAuth } from "@/hooks/useAuth";
import { api } from "@/lib/api";
import { AppShell } from "@/components/layout/AppShell";
import { BookingsSidebar } from "@/components/bookings/BookingsSidebar";
import type { Booking, AvailabilitySlot, AvailableTime, SessionBriefing } from "@/lib/types";

// ── Day names ─────────────────────────────────────────────────────────
const DAY_NAMES = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"];
const DAY_SHORT = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"];

// ── Status config ─────────────────────────────────────────────────────
const STATUS_CONFIG: Record<string, { label: string; color: string; bg: string }> = {
  requested: { label: "Ausstehend", color: "text-amber-600", bg: "bg-amber-50 border border-amber-200" },
  confirmed: { label: "Bestaetigt", color: "text-green-600", bg: "bg-green-50 border border-green-200" },
  cancelled: { label: "Abgesagt", color: "text-red-600", bg: "bg-red-50 border border-red-200" },
  completed: { label: "Abgeschlossen", color: "text-blue-600", bg: "bg-blue-50 border border-blue-200" },
  no_show: { label: "Nicht erschienen", color: "text-slate-500", bg: "bg-slate-50 border border-slate-200" },
};

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
  const statusCfg = STATUS_CONFIG[booking.status] ?? STATUS_CONFIG.requested;
  const partnerName = isCoach
    ? booking.coachee_name ?? "Coachee"
    : booking.coach_name ?? "Coach";

  return (
    <div className="glass-card-interactive p-5">
      <div className="flex items-start justify-between mb-3">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className={`text-xs px-2 py-0.5 rounded-full ${statusCfg.bg} ${statusCfg.color}`}>
              {statusCfg.label}
            </span>
            {booking.has_briefing && isCoach && (
              <span className="text-xs px-2 py-0.5 rounded-full bg-purple-400/10 border border-purple-400/20 text-purple-600">
                Briefing
              </span>
            )}
          </div>
          <h3 className="text-slate-900 font-medium">
            {booking.topic ?? "Coaching-Session"}
          </h3>
          <p className="text-sm text-slate-500">mit {partnerName}</p>
        </div>
        <div className="text-right">
          <div className="text-sm text-slate-900 font-medium">{dateStr}</div>
          <div className="text-sm text-scil">{timeStr} Uhr</div>
          <div className="text-xs text-slate-500">{booking.duration_minutes} Min.</div>
        </div>
      </div>

      {booking.coachee_notes && (
        <div className="text-xs text-slate-500 bg-black/[0.02] border border-black/[0.06] rounded-xl p-3 mb-3">
          <span className="text-slate-500">Notiz:</span> {booking.coachee_notes}
        </div>
      )}

      {booking.summary && (
        <div className="text-xs text-slate-500 bg-black/[0.02] border border-black/[0.06] rounded-xl p-3 mb-3">
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
            className="px-3 py-1.5 text-xs bg-green-500/10 text-green-600 hover:bg-green-500/20 rounded-xl border border-green-500/20 transition-colors"
          >
            Bestaetigen
          </button>
        )}
        {booking.status === "confirmed" && isCoach && (
          <button
            onClick={() => onComplete(booking.id)}
            className="px-3 py-1.5 text-xs bg-blue-500/10 text-blue-600 hover:bg-blue-500/20 rounded-xl border border-blue-500/20 transition-colors"
          >
            Abschliessen
          </button>
        )}
        {(booking.status === "requested" || booking.status === "confirmed") && (
          <button
            onClick={() => onCancel(booking.id)}
            className="px-3 py-1.5 text-xs bg-red-500/10 text-red-600 hover:bg-red-500/20 rounded-xl border border-red-500/20 transition-colors"
          >
            Absagen
          </button>
        )}
        {isCoach && booking.has_briefing && (
          <button
            onClick={() => onViewBriefing(booking.id)}
            className="px-3 py-1.5 text-xs bg-purple-500/10 text-purple-600 hover:bg-purple-500/20 rounded-xl border border-purple-500/20 transition-colors"
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
  onUpdateSlot,
}: {
  slots: AvailabilitySlot[];
  onCreateSlot: (slot: {
    day_of_week: number;
    start_time: string;
    end_time: string;
    duration_minutes: number;
  }) => Promise<void>;
  onDeleteSlot: (id: string) => Promise<void>;
  onUpdateSlot: (slotId: string, updates: Partial<{
    start_time: string; end_time: string; duration_minutes: number;
    recurrence: string; notes: string; is_active: boolean;
  }>) => Promise<void>;
}) {
  const [showForm, setShowForm] = useState(false);
  const [dayOfWeek, setDayOfWeek] = useState(0);
  const [startTime, setStartTime] = useState("09:00");
  const [endTime, setEndTime] = useState("12:00");
  const [duration, setDuration] = useState(60);
  const [creating, setCreating] = useState(false);
  const [editingSlot, setEditingSlot] = useState<AvailabilitySlot | null>(null);
  const [editStartTime, setEditStartTime] = useState("");
  const [editEndTime, setEditEndTime] = useState("");
  const [editDuration, setEditDuration] = useState(60);
  const [saving, setSaving] = useState(false);

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

  const handleEditClick = (slot: AvailabilitySlot) => {
    setEditingSlot(slot);
    setEditStartTime(slot.start_time);
    setEditEndTime(slot.end_time);
    setEditDuration(slot.duration_minutes);
  };

  const handleEditCancel = () => {
    setEditingSlot(null);
  };

  const handleEditSave = async () => {
    if (!editingSlot) return;
    setSaving(true);
    try {
      await onUpdateSlot(editingSlot.id, {
        start_time: editStartTime,
        end_time: editEndTime,
        duration_minutes: editDuration,
      });
      setEditingSlot(null);
    } finally {
      setSaving(false);
    }
  };

  const slotsByDay: Record<number, AvailabilitySlot[]> = {};
  slots.forEach((s) => {
    if (!slotsByDay[s.day_of_week]) slotsByDay[s.day_of_week] = [];
    slotsByDay[s.day_of_week].push(s);
  });

  return (
    <div className="glass-card p-5 animate-fade-in-up">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-slate-900">Verfuegbarkeit</h2>
        <button
          onClick={() => setShowForm(!showForm)}
          className="btn-glass text-white font-medium rounded-xl px-3 py-1.5 text-sm"
        >
          {showForm ? "Abbrechen" : "+ Slot hinzufuegen"}
        </button>
      </div>

      {showForm && (
        <div className="bg-black/[0.02] border border-black/[0.06] rounded-xl p-4 mb-4 space-y-3 animate-fade-in-up">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs text-slate-500 mb-1">Tag</label>
              <select
                value={dayOfWeek}
                onChange={(e) => setDayOfWeek(Number(e.target.value))}
                className="glass-input text-slate-900 px-3 py-2.5 w-full text-sm"
              >
                {DAY_NAMES.map((name, i) => (
                  <option key={i} value={i}>{name}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs text-slate-500 mb-1">Dauer (Min.)</label>
              <select
                value={duration}
                onChange={(e) => setDuration(Number(e.target.value))}
                className="glass-input text-slate-900 px-3 py-2.5 w-full text-sm"
              >
                <option value={30}>30</option>
                <option value={45}>45</option>
                <option value={60}>60</option>
                <option value={90}>90</option>
              </select>
            </div>
            <div>
              <label className="block text-xs text-slate-500 mb-1">Von</label>
              <input
                type="time"
                value={startTime}
                onChange={(e) => setStartTime(e.target.value)}
                className="glass-input text-slate-900 px-3 py-2.5 w-full text-sm"
              />
            </div>
            <div>
              <label className="block text-xs text-slate-500 mb-1">Bis</label>
              <input
                type="time"
                value={endTime}
                onChange={(e) => setEndTime(e.target.value)}
                className="glass-input text-slate-900 px-3 py-2.5 w-full text-sm"
              />
            </div>
          </div>
          <button
            onClick={handleCreate}
            disabled={creating}
            className="btn-glass text-white font-medium rounded-xl w-full py-2 text-sm disabled:opacity-50"
          >
            {creating ? "Erstelle..." : "Slot erstellen"}
          </button>
        </div>
      )}

      {/* Edit Slot Form */}
      {editingSlot && (
        <div className="bg-black/[0.02] border border-black/[0.06] rounded-xl p-4 mb-4 space-y-3 animate-fade-in-up">
          <h3 className="text-sm font-medium text-slate-700">Slot bearbeiten</h3>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs text-slate-500 mb-1">Tag</label>
              <select
                value={editingSlot.day_of_week}
                disabled
                className="glass-input text-slate-900 px-3 py-2.5 w-full text-sm opacity-60 cursor-not-allowed"
              >
                {DAY_NAMES.map((name, i) => (
                  <option key={i} value={i}>{name}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs text-slate-500 mb-1">Dauer (Min.)</label>
              <select
                value={editDuration}
                onChange={(e) => setEditDuration(Number(e.target.value))}
                className="glass-input text-slate-900 px-3 py-2.5 w-full text-sm"
              >
                <option value={30}>30</option>
                <option value={45}>45</option>
                <option value={60}>60</option>
                <option value={90}>90</option>
              </select>
            </div>
            <div>
              <label className="block text-xs text-slate-500 mb-1">Von</label>
              <input
                type="time"
                value={editStartTime}
                onChange={(e) => setEditStartTime(e.target.value)}
                className="glass-input text-slate-900 px-3 py-2.5 w-full text-sm"
              />
            </div>
            <div>
              <label className="block text-xs text-slate-500 mb-1">Bis</label>
              <input
                type="time"
                value={editEndTime}
                onChange={(e) => setEditEndTime(e.target.value)}
                className="glass-input text-slate-900 px-3 py-2.5 w-full text-sm"
              />
            </div>
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleEditSave}
              disabled={saving}
              className="btn-glass text-white font-medium rounded-xl flex-1 py-2 text-sm disabled:opacity-50"
            >
              {saving ? "Speichere..." : "Speichern"}
            </button>
            <button
              onClick={handleEditCancel}
              className="btn-ghost text-slate-600 rounded-xl px-4 py-2 text-sm"
            >
              Abbrechen
            </button>
          </div>
        </div>
      )}

      <div className="grid grid-cols-7 gap-1">
        {DAY_SHORT.map((day, i) => (
          <div key={i} className="text-center">
            <div className="text-xs text-slate-500 font-medium mb-2">{day}</div>
            <div className="space-y-1 min-h-[60px]">
              {(slotsByDay[i] ?? []).map((slot) => (
                <div
                  key={slot.id}
                  onClick={() => handleEditClick(slot)}
                  className="group relative bg-scil/10 border border-scil/20 rounded-xl px-1 py-1 text-center cursor-pointer hover:bg-scil/20 transition-colors"
                >
                  <div className="text-[10px] text-scil leading-tight">{slot.start_time}</div>
                  <div className="text-[10px] text-scil leading-tight">{slot.end_time}</div>
                  <button
                    onClick={(e) => { e.stopPropagation(); onDeleteSlot(slot.id); }}
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
  onRefresh,
}: {
  briefing: SessionBriefing;
  onClose: () => void;
  onRegenerate: () => void;
  onRefresh?: () => void;
}) {
  // Auto-refresh polling when briefing is generating
  useEffect(() => {
    if (briefing.status !== "generating" || !onRefresh) return;
    const interval = setInterval(() => {
      onRefresh();
    }, 3000);
    return () => clearInterval(interval);
  }, [briefing.status, onRefresh]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center modal-backdrop">
      <div className="glass-strong rounded-2xl animate-fade-in-up max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-slate-900">Session Briefing</h2>
            <button onClick={onClose} className="text-slate-500 hover:text-slate-900 text-xl">x</button>
          </div>

          {briefing.status === "generating" ? (
            <div className="text-center py-8">
              <div className="animate-spin w-8 h-8 border-2 border-scil border-t-transparent rounded-full mx-auto mb-3" />
              <p className="text-slate-500">Briefing wird generiert...</p>
            </div>
          ) : (
            <div className="space-y-4">
              {briefing.coachee_profile_summary && (
                <div>
                  <h3 className="text-sm font-medium text-slate-600 mb-1">Coachee-Profil</h3>
                  <p className="text-sm text-slate-500 bg-black/[0.02] border border-black/[0.06] rounded-xl p-3">{briefing.coachee_profile_summary}</p>
                </div>
              )}
              {briefing.scil_highlights && (
                <div>
                  <h3 className="text-sm font-medium text-slate-600 mb-1">SCIL Highlights</h3>
                  <div className="bg-black/[0.02] border border-black/[0.06] rounded-xl p-3">
                    {Object.entries(briefing.scil_highlights).map(([key, val]) => (
                      <div key={key} className="flex justify-between text-sm py-0.5">
                        <span className="text-slate-500 capitalize">{key}</span>
                        <span className="text-slate-900">{String(val)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              {briefing.suggested_topics && briefing.suggested_topics.length > 0 && (
                <div>
                  <h3 className="text-sm font-medium text-slate-600 mb-1">Vorgeschlagene Themen</h3>
                  <ul className="space-y-1">
                    {briefing.suggested_topics.map((topic, i) => (
                      <li key={i} className="text-sm text-slate-500 bg-black/[0.02] border border-black/[0.06] rounded-xl px-3 py-2">{topic}</li>
                    ))}
                  </ul>
                </div>
              )}
              {briefing.suggested_exercises && briefing.suggested_exercises.length > 0 && (
                <div>
                  <h3 className="text-sm font-medium text-slate-600 mb-1">Vorgeschlagene Uebungen</h3>
                  <ul className="space-y-1">
                    {briefing.suggested_exercises.map((ex, i) => (
                      <li key={i} className="text-sm text-slate-500 bg-black/[0.02] border border-black/[0.06] rounded-xl px-3 py-2">{ex}</li>
                    ))}
                  </ul>
                </div>
              )}
              {briefing.previous_session_notes && (
                <div>
                  <h3 className="text-sm font-medium text-slate-600 mb-1">Vorherige Sessions</h3>
                  <p className="text-sm text-slate-500 bg-black/[0.02] border border-black/[0.06] rounded-xl p-3">{briefing.previous_session_notes}</p>
                </div>
              )}
              {briefing.training_progress_summary && (
                <div>
                  <h3 className="text-sm font-medium text-slate-600 mb-1">Trainingsfortschritt</h3>
                  <p className="text-sm text-slate-500 bg-black/[0.02] border border-black/[0.06] rounded-xl p-3">{briefing.training_progress_summary}</p>
                </div>
              )}
              {briefing.content && (
                <div>
                  <h3 className="text-sm font-medium text-slate-600 mb-1">Briefing</h3>
                  <div className="text-sm text-slate-500 bg-black/[0.02] border border-black/[0.06] rounded-xl p-3 whitespace-pre-wrap">{briefing.content}</div>
                </div>
              )}
            </div>
          )}

          <div className="flex gap-2 mt-6">
            <button onClick={onRegenerate} className="px-4 py-2 text-sm bg-purple-500/10 text-purple-600 hover:bg-purple-500/20 rounded-xl border border-purple-500/20 transition-colors">
              Neu generieren
            </button>
            <button onClick={onClose} className="btn-ghost text-slate-600 rounded-xl px-4 py-2 text-sm">
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
  fetchAvailableTimes,
}: {
  coachId: string;
  onClose: () => void;
  onBook: (data: { coach_id: string; scheduled_at: string; topic?: string; coachee_notes?: string; slot_id?: string }) => Promise<void>;
  fetchAvailableTimes?: (coachId: string, startDate: string, endDate: string) => Promise<AvailableTime[]>;
}) {
  const [date, setDate] = useState("");
  const [time, setTime] = useState("09:00");
  const [topic, setTopic] = useState("");
  const [notes, setNotes] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [availableSlots, setAvailableSlots] = useState<AvailableTime[]>([]);
  const [loadingSlots, setLoadingSlots] = useState(false);

  // Fetch available times when coachId is set
  useEffect(() => {
    if (!coachId || !fetchAvailableTimes) return;
    setLoadingSlots(true);
    const start = new Date();
    const end = new Date();
    end.setDate(end.getDate() + 14);
    fetchAvailableTimes(
      coachId,
      start.toISOString().split("T")[0],
      end.toISOString().split("T")[0]
    )
      .then((times) => setAvailableSlots(times))
      .catch(() => {})
      .finally(() => setLoadingSlots(false));
  }, [coachId, fetchAvailableTimes]);

  const handleSelectSlot = (slot: AvailableTime) => {
    setDate(slot.date);
    setTime(slot.time);
  };

  const handleSubmit = async () => {
    if (!date || !time) return;
    setSubmitting(true);
    try {
      const scheduled = `${date}T${time}:00`;
      await onBook({ coach_id: coachId, scheduled_at: scheduled, topic: topic || undefined, coachee_notes: notes || undefined });
      onClose();
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center modal-backdrop">
      <div className="glass-strong rounded-2xl animate-fade-in-up max-w-md w-full mx-4 p-6">
        <h2 className="text-lg font-semibold text-slate-900 mb-4">Neue Buchung</h2>

        {!coachId ? (
          <div className="text-center py-6">
            <p className="text-slate-500 text-sm mb-2">Kein Coach zugewiesen.</p>
            <p className="text-slate-500 text-xs">Bitte wende dich an deinen Coach, um eine Einladung zu erhalten.</p>
            <button onClick={onClose} className="mt-4 btn-ghost text-slate-600 rounded-xl px-4 py-2 text-sm">Schliessen</button>
          </div>
        ) : (
          <>
            {/* Available time slots from coach */}
            {availableSlots.length > 0 && (
              <div className="mb-4">
                <label className="block text-xs text-slate-500 mb-2">Verfuegbare Termine</label>
                <div className="max-h-40 overflow-y-auto space-y-1">
                  {availableSlots.slice(0, 20).map((slot, i) => {
                    const slotDate = new Date(slot.date + "T" + slot.time);
                    const isSelected = date === slot.date && time === slot.time;
                    return (
                      <button
                        key={i}
                        type="button"
                        onClick={() => handleSelectSlot(slot)}
                        className={`w-full text-left px-3 py-2 rounded-xl text-sm transition-colors ${
                          isSelected
                            ? "bg-scil/10 border border-scil/30 text-scil"
                            : "bg-black/[0.02] border border-black/[0.06] text-slate-700 hover:bg-black/[0.04]"
                        }`}
                      >
                        {slotDate.toLocaleDateString("de-DE", { weekday: "short", day: "2-digit", month: "2-digit" })}
                        {" "}
                        <span className="font-medium">{slot.time} ({slot.duration_minutes} Min.)</span>
                      </button>
                    );
                  })}
                </div>
              </div>
            )}
            {loadingSlots && (
              <div className="text-center py-3 mb-3">
                <div className="animate-spin w-5 h-5 border-2 border-scil border-t-transparent rounded-full mx-auto" />
                <p className="text-xs text-slate-500 mt-1">Lade verfuegbare Zeiten...</p>
              </div>
            )}

            {/* Manual date/time (fallback or fine-tuning) */}
            <div className="space-y-3">
              <div>
                <label className="block text-xs text-slate-500 mb-1">{availableSlots.length > 0 ? "Datum (oder manuell waehlen)" : "Datum"}</label>
                <input type="date" value={date} onChange={(e) => setDate(e.target.value)} className="glass-input text-slate-900 px-3 py-2.5 w-full text-sm" />
              </div>
              <div>
                <label className="block text-xs text-slate-500 mb-1">Uhrzeit</label>
                <input type="time" value={time} onChange={(e) => setTime(e.target.value)} className="glass-input text-slate-900 px-3 py-2.5 w-full text-sm" />
              </div>
              <div>
                <label className="block text-xs text-slate-500 mb-1">Thema (optional)</label>
                <input type="text" value={topic} onChange={(e) => setTopic(e.target.value)} placeholder="z.B. Kommunikation verbessern" className="glass-input text-slate-900 px-3 py-2.5 w-full text-sm placeholder:text-slate-500" />
              </div>
              <div>
                <label className="block text-xs text-slate-500 mb-1">Notizen (optional)</label>
                <textarea value={notes} onChange={(e) => setNotes(e.target.value)} rows={3} placeholder="Was moechtest du besprechen?" className="glass-input text-slate-900 px-3 py-2.5 w-full text-sm placeholder:text-slate-500 resize-none" />
              </div>
            </div>
            <div className="flex gap-2 mt-5">
              <button onClick={handleSubmit} disabled={!date || submitting} className="btn-glass text-white font-medium rounded-xl flex-1 py-2 text-sm disabled:opacity-50">
                {submitting ? "Buche..." : "Buchen"}
              </button>
              <button onClick={onClose} className="btn-ghost text-slate-600 rounded-xl px-4 py-2 text-sm">Abbrechen</button>
            </div>
          </>
        )}
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
    try { await onComplete(coachNotes, summary); onClose(); } finally { setSubmitting(false); }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center modal-backdrop">
      <div className="glass-strong rounded-2xl animate-fade-in-up max-w-md w-full mx-4 p-6">
        <h2 className="text-lg font-semibold text-slate-900 mb-4">Session abschliessen</h2>
        <div className="space-y-3">
          <div>
            <label className="block text-xs text-slate-500 mb-1">Coach-Notizen</label>
            <textarea value={coachNotes} onChange={(e) => setCoachNotes(e.target.value)} rows={3} placeholder="Interne Notizen zur Session..." className="glass-input text-slate-900 px-3 py-2.5 w-full text-sm placeholder:text-slate-500 resize-none" />
          </div>
          <div>
            <label className="block text-xs text-slate-500 mb-1">Zusammenfassung</label>
            <textarea value={summary} onChange={(e) => setSummary(e.target.value)} rows={3} placeholder="Oeffentliche Zusammenfassung der Session..." className="glass-input text-slate-900 px-3 py-2.5 w-full text-sm placeholder:text-slate-500 resize-none" />
          </div>
        </div>
        <div className="flex gap-2 mt-5">
          <button onClick={handleSubmit} disabled={submitting} className="btn-glass text-white font-medium rounded-xl flex-1 py-2 text-sm disabled:opacity-50">
            {submitting ? "Speichere..." : "Abschliessen"}
          </button>
          <button onClick={onClose} className="btn-ghost text-slate-600 rounded-xl px-4 py-2 text-sm">Abbrechen</button>
        </div>
      </div>
    </div>
  );
}

// ══════════════════════════════════════════════════════════════════════
// Main Page
// ══════════════════════════════════════════════════════════════════════
export default function BookingsPage() {
  const { user } = useAuth();
  const {
    slots, bookings, upcomingBookings, currentBriefing,
    isLoading, error, clearError, fetchSlots, createSlot, deleteSlot, updateSlot,
    fetchBookings, fetchUpcoming, confirmBooking, cancelBooking, completeBooking,
    createBooking, fetchBriefing, regenerateBriefing, fetchAvailableTimes,
  } = useBookings();

  const [activeTab, setActiveTab] = useState<"upcoming" | "all" | "slots">("upcoming");
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [showNewBooking, setShowNewBooking] = useState(false);
  const [showBriefing, setShowBriefing] = useState(false);
  const [briefingBookingId, setBriefingBookingId] = useState<string | null>(null);
  const [showComplete, setShowComplete] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [myCoachId, setMyCoachId] = useState<string>("");

  const isCoach = user?.role === "coach" || user?.role === "admin";

  // Fetch assigned coach for coachees (needed for booking creation)
  useEffect(() => {
    if (!isCoach) {
      api
        .get<{ coach_id: string; coach_name: string }>("/me/coach")
        .then((data) => {
          if (data?.coach_id) setMyCoachId(data.coach_id);
        })
        .catch(() => {});
    }
  }, [isCoach]);

  // Refresh bookings when filter changes
  useEffect(() => {
    if (activeTab === "all") {
      fetchBookings(isCoach ? "coach" : undefined, statusFilter || undefined);
    }
  }, [activeTab, statusFilter, isCoach, fetchBookings]);

  const pendingCount = bookings.filter((b) => b.status === "requested").length;
  const confirmedCount = bookings.filter((b) => b.status === "confirmed").length;
  const completedCount = bookings.filter((b) => b.status === "completed").length;

  const handleConfirm = async (id: string) => {
    setActionLoading(true);
    try { await confirmBooking(id); fetchUpcoming(); } catch (e) { console.error(e); } finally { setActionLoading(false); }
  };

  const handleCancel = async (id: string) => {
    setActionLoading(true);
    try { await cancelBooking(id); fetchUpcoming(); } catch (e) { console.error(e); } finally { setActionLoading(false); }
  };

  const handleComplete = async (id: string) => { setShowComplete(id); };

  const handleCompleteSubmit = async (notes: string, summary: string) => {
    if (!showComplete) return;
    setActionLoading(true);
    try { await completeBooking(showComplete, { coach_notes: notes || undefined, summary: summary || undefined }); fetchUpcoming(); setShowComplete(null); } catch (e) { console.error(e); } finally { setActionLoading(false); }
  };

  const handleViewBriefing = async (bookingId: string) => {
    try { await fetchBriefing(bookingId); setBriefingBookingId(bookingId); setShowBriefing(true); } catch (e) { console.error(e); }
  };

  const handleRefreshBriefing = async () => {
    if (briefingBookingId) {
      try { await fetchBriefing(briefingBookingId); } catch (e) { console.error(e); }
    }
  };

  const handleCreateBooking = async (data: { coach_id: string; scheduled_at: string; topic?: string; coachee_notes?: string; slot_id?: string }) => {
    await createBooking(data); fetchUpcoming(); fetchBookings();
  };

  const handleCreateSlot = async (slot: { day_of_week: number; start_time: string; end_time: string; duration_minutes: number }) => { await createSlot(slot); };
  const handleDeleteSlot = async (id: string) => { await deleteSlot(id); };

  const handleRegenerate = async () => {
    if (currentBriefing) {
      const bookingId = bookings.find((b) => b.has_briefing)?.id;
      if (bookingId) { await regenerateBriefing(bookingId); }
    }
  };

  return (
    <>
      <AppShell
        leftSidebar={
          <BookingsSidebar
            statusFilter={statusFilter}
            onStatusFilter={setStatusFilter}
            upcomingBookings={upcomingBookings}
            pendingCount={pendingCount}
            confirmedCount={confirmedCount}
            completedCount={completedCount}
            isCoach={isCoach}
            slotsCount={slots.length}
            onNewBooking={() => setShowNewBooking(true)}
          />
        }
        rightDefaultOpen={false}
      >
        <div className="w-full px-6 py-6 space-y-6 animate-fade-in-up">
          {/* Error banner */}
          {error && (
            <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 flex items-center justify-between">
              <span className="text-sm text-red-600">{error}</span>
              <button onClick={clearError} className="text-red-600 hover:text-red-300 text-sm">x</button>
            </div>
          )}

          {/* Tabs */}
          <div className="flex gap-1 bg-black/[0.02] border border-black/[0.06] rounded-xl p-1">
            <button
              onClick={() => setActiveTab("upcoming")}
              className={`flex-1 px-4 py-2 text-sm rounded-lg transition-colors ${activeTab === "upcoming" ? "nav-pill-active text-scil" : "text-slate-500 hover:bg-black/[0.04] hover:text-slate-900"}`}
            >
              Naechste Sessions
            </button>
            <button
              onClick={() => setActiveTab("all")}
              className={`flex-1 px-4 py-2 text-sm rounded-lg transition-colors ${activeTab === "all" ? "nav-pill-active text-scil" : "text-slate-500 hover:bg-black/[0.04] hover:text-slate-900"}`}
            >
              Alle Buchungen
            </button>
            {isCoach && (
              <button
                onClick={() => setActiveTab("slots")}
                className={`flex-1 px-4 py-2 text-sm rounded-lg transition-colors ${activeTab === "slots" ? "nav-pill-active text-scil" : "text-slate-500 hover:bg-black/[0.04] hover:text-slate-900"}`}
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
                <div className="text-center py-12 glass-card animate-fade-in-up">
                  <p className="text-slate-500 mb-2">Keine kommenden Sessions</p>
                  {!isCoach && (
                    <button onClick={() => setShowNewBooking(true)} className="text-sm text-scil hover:text-scil-light">
                      Jetzt eine Session buchen
                    </button>
                  )}
                </div>
              ) : (
                upcomingBookings.map((b, i) => (
                  <div key={b.id} className={`animate-fade-in-up stagger-${Math.min(i + 1, 6)}`}>
                    <BookingCard booking={b} isCoach={isCoach} onConfirm={handleConfirm} onCancel={handleCancel} onComplete={handleComplete} onViewBriefing={handleViewBriefing} />
                  </div>
                ))
              )}
            </div>
          )}

          {activeTab === "all" && (
            <div className="space-y-4">
              {isLoading ? (
                <div className="text-center py-12">
                  <div className="animate-spin w-8 h-8 border-2 border-scil border-t-transparent rounded-full mx-auto" />
                </div>
              ) : bookings.length === 0 ? (
                <div className="text-center py-12 glass-card animate-fade-in-up">
                  <p className="text-slate-500">Keine Buchungen gefunden</p>
                </div>
              ) : (
                bookings.map((b, i) => (
                  <div key={b.id} className={`animate-fade-in-up stagger-${Math.min(i + 1, 6)}`}>
                    <BookingCard booking={b} isCoach={isCoach} onConfirm={handleConfirm} onCancel={handleCancel} onComplete={handleComplete} onViewBriefing={handleViewBriefing} />
                  </div>
                ))
              )}
            </div>
          )}

          {activeTab === "slots" && isCoach && (
            <SlotManager slots={slots} onCreateSlot={handleCreateSlot} onDeleteSlot={handleDeleteSlot} onUpdateSlot={async (id, u) => { await updateSlot(id, u); }} />
          )}
        </div>
      </AppShell>

      {/* Modals */}
      {showNewBooking && (
        <NewBookingModal coachId={myCoachId} onClose={() => setShowNewBooking(false)} onBook={handleCreateBooking} fetchAvailableTimes={fetchAvailableTimes} />
      )}
      {showBriefing && currentBriefing && (
        <BriefingPanel briefing={currentBriefing} onClose={() => { setShowBriefing(false); setBriefingBookingId(null); }} onRegenerate={handleRegenerate} onRefresh={handleRefreshBriefing} />
      )}
      {showComplete && (
        <CompleteModal onClose={() => setShowComplete(null)} onComplete={handleCompleteSubmit} />
      )}
      {actionLoading && (
        <div className="fixed inset-0 z-40 modal-backdrop flex items-center justify-center">
          <div className="animate-spin w-8 h-8 border-2 border-scil border-t-transparent rounded-full" />
        </div>
      )}
    </>
  );
}
