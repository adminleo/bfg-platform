"use client";

import type { Booking } from "@/lib/types";

const STATUS_CONFIG: Record<string, { label: string; color: string; bg: string }> = {
  requested: { label: "Ausstehend", color: "text-amber-400", bg: "bg-amber-400/10" },
  confirmed: { label: "Bestaetigt", color: "text-green-400", bg: "bg-green-400/10" },
  cancelled: { label: "Abgesagt", color: "text-red-400", bg: "bg-red-400/10" },
  completed: { label: "Abgeschlossen", color: "text-blue-400", bg: "bg-blue-400/10" },
  no_show: { label: "Nicht erschienen", color: "text-slate-400", bg: "bg-slate-400/10" },
};

interface BookingsSidebarProps {
  statusFilter: string;
  onStatusFilter: (status: string) => void;
  upcomingBookings: Booking[];
  pendingCount: number;
  confirmedCount: number;
  completedCount: number;
  isCoach: boolean;
  slotsCount: number;
  onNewBooking: () => void;
}

export function BookingsSidebar({
  statusFilter,
  onStatusFilter,
  upcomingBookings,
  pendingCount,
  confirmedCount,
  completedCount,
  isCoach,
  slotsCount,
  onNewBooking,
}: BookingsSidebarProps) {
  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-4">
        <div className="flex items-center gap-2 mb-1">
          <svg className="w-5 h-5 text-scil" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          <h2 className="text-sm font-semibold text-white">Buchungen</h2>
        </div>
      </div>

      {/* Stats */}
      <div className="px-4 pb-3 grid grid-cols-2 gap-2">
        <div className="bg-white/[0.03] border border-white/[0.06] rounded-xl p-2.5">
          <div className="text-lg font-bold text-amber-400 stat-number">{pendingCount}</div>
          <div className="text-[10px] text-slate-500">Ausstehend</div>
        </div>
        <div className="bg-white/[0.03] border border-white/[0.06] rounded-xl p-2.5">
          <div className="text-lg font-bold text-green-400 stat-number">{confirmedCount}</div>
          <div className="text-[10px] text-slate-500">Bestaetigt</div>
        </div>
        <div className="bg-white/[0.03] border border-white/[0.06] rounded-xl p-2.5">
          <div className="text-lg font-bold text-blue-400 stat-number">{completedCount}</div>
          <div className="text-[10px] text-slate-500">Abgeschlossen</div>
        </div>
        <div className="bg-white/[0.03] border border-white/[0.06] rounded-xl p-2.5">
          <div className="text-lg font-bold text-white stat-number">{isCoach ? slotsCount : (upcomingBookings.length > 0 ? upcomingBookings.length : "--")}</div>
          <div className="text-[10px] text-slate-500">{isCoach ? "Slots" : "Kommend"}</div>
        </div>
      </div>

      {/* Status filter */}
      <div className="px-4 pb-3">
        <div className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-2">Filter</div>
        <div className="flex flex-wrap gap-1.5">
          {["", "requested", "confirmed", "completed", "cancelled"].map((st) => (
            <button
              key={st}
              onClick={() => onStatusFilter(st)}
              className={`px-2.5 py-1 text-[10px] rounded-full transition-all duration-200 ${
                statusFilter === st
                  ? "bg-scil text-white shadow-glow-sm"
                  : "bg-white/[0.03] text-slate-400 hover:text-white border border-white/[0.06]"
              }`}
            >
              {st === "" ? "Alle" : STATUS_CONFIG[st]?.label ?? st}
            </button>
          ))}
        </div>
      </div>

      {/* Upcoming mini list */}
      <div className="px-4 pb-3 flex-1 overflow-y-auto">
        <div className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-2">
          Naechste Sessions
        </div>
        {upcomingBookings.length === 0 ? (
          <p className="text-xs text-slate-500 text-center py-4">Keine kommenden Sessions</p>
        ) : (
          <div className="space-y-1.5">
            {upcomingBookings.slice(0, 5).map((b) => {
              const dt = new Date(b.scheduled_at);
              const dateStr = dt.toLocaleDateString("de-DE", { day: "2-digit", month: "2-digit" });
              const timeStr = dt.toLocaleTimeString("de-DE", { hour: "2-digit", minute: "2-digit" });
              const statusCfg = STATUS_CONFIG[b.status];
              return (
                <div key={b.id} className="bg-white/[0.03] border border-white/[0.06] rounded-xl p-2.5">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-medium text-white truncate">
                      {b.topic || "Coaching-Session"}
                    </span>
                    <span className={`text-[10px] ${statusCfg?.color || "text-slate-400"}`}>
                      {statusCfg?.label || b.status}
                    </span>
                  </div>
                  <div className="text-[10px] text-slate-500 mt-0.5">
                    {dateStr} &middot; {timeStr} Uhr &middot; {b.duration_minutes} Min.
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* New booking button */}
      {!isCoach && (
        <div className="p-4 border-t border-white/[0.06]">
          <button
            onClick={onNewBooking}
            className="w-full px-3 py-2 btn-glass text-white text-xs font-medium rounded-xl transition-all"
          >
            + Neue Buchung
          </button>
        </div>
      )}
    </div>
  );
}
