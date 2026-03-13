"use client";

import { useState } from "react";
import type { Session } from "@/lib/types";

interface LeftSidebarProps {
  sessions: Session[];
  activeSessionId: string | null;
  onCreateSession: () => void;
  onSelectSession: (id: string) => void;
  onDeleteSession: (id: string) => void;
  onLogout: () => void;
  isLoading: boolean;
  userRole?: string;
}

export function LeftSidebar({
  sessions,
  activeSessionId,
  onCreateSession,
  onSelectSession,
  onDeleteSession,
  onLogout,
  isLoading,
  userRole,
}: LeftSidebarProps) {
  const isCoach = userRole === "coach" || userRole === "admin";
  const [menuOpenId, setMenuOpenId] = useState<string | null>(null);

  // Group sessions by date
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);

  const todaySessions = sessions.filter(
    (s) => new Date(s.created_at) >= today
  );
  const weekSessions = sessions.filter((s) => {
    const d = new Date(s.created_at);
    return d < today && d >= weekAgo;
  });
  const olderSessions = sessions.filter(
    (s) => new Date(s.created_at) < weekAgo
  );

  const renderSession = (session: Session) => {
    const isActive = session.id === activeSessionId;
    const statusIcon =
      session.status === "completed" ? "✓" :
      session.status === "in_progress" ? "●" : "○";
    const statusColor =
      session.status === "completed" ? "text-green-400" :
      session.status === "in_progress" ? "text-scil" : "text-slate-500";

    return (
      <div
        key={session.id}
        className={`group flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer transition-colors ${
          isActive
            ? "bg-surface-hover text-white"
            : "text-slate-400 hover:bg-surface hover:text-slate-200"
        }`}
        onClick={() => onSelectSession(session.id)}
      >
        <span className={`text-xs ${statusColor}`}>{statusIcon}</span>
        <span className="flex-1 text-sm truncate">
          {session.title || `Diagnostik`}
        </span>
        <button
          className="opacity-0 group-hover:opacity-100 p-1 hover:text-red-400 transition-opacity"
          onClick={(e) => {
            e.stopPropagation();
            setMenuOpenId(menuOpenId === session.id ? null : session.id);
          }}
          title="Optionen"
        >
          ⋯
        </button>
        {menuOpenId === session.id && (
          <div className="absolute right-2 mt-16 bg-surface-dark border border-border rounded-lg shadow-xl py-1 z-50">
            <button
              className="block w-full text-left px-4 py-2 text-sm text-red-400 hover:bg-surface-hover"
              onClick={(e) => {
                e.stopPropagation();
                onDeleteSession(session.id);
                setMenuOpenId(null);
              }}
            >
              Loeschen
            </button>
          </div>
        )}
      </div>
    );
  };

  const renderGroup = (label: string, items: Session[]) => {
    if (items.length === 0) return null;
    return (
      <div className="mb-4">
        <div className="px-3 py-1 text-xs font-medium text-slate-500 uppercase tracking-wider">
          {label}
        </div>
        {items.map(renderSession)}
      </div>
    );
  };

  return (
    <div className="flex flex-col h-full bg-surface-dark">
      {/* Header */}
      <div className="p-4 border-b border-border">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-8 h-8 rounded-lg bg-scil flex items-center justify-center text-white font-bold text-sm">
            S
          </div>
          <span className="font-semibold text-white">S.C.I.L. Profile</span>
        </div>

        <button
          onClick={onCreateSession}
          disabled={isLoading}
          className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-scil hover:bg-scil-dark text-white rounded-lg font-medium transition-colors disabled:opacity-50"
        >
          <span className="text-lg">+</span>
          <span>Neue Diagnostik</span>
        </button>
      </div>

      {/* Session List */}
      <div className="flex-1 overflow-y-auto p-2">
        {sessions.length === 0 ? (
          <div className="text-center text-slate-500 text-sm mt-8 px-4">
            Starte deine erste SCIL-Diagnostik!
          </div>
        ) : (
          <>
            {renderGroup("Heute", todaySessions)}
            {renderGroup("Letzte 7 Tage", weekSessions)}
            {renderGroup("Aelter", olderSessions)}
          </>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-border space-y-1">
        {isCoach && (
          <a
            href="/coach"
            className="block w-full text-left px-3 py-2 text-sm text-scil hover:text-scil-light hover:bg-surface rounded-lg transition-colors"
          >
            Coach Dashboard
          </a>
        )}
        <a
          href="/training"
          className="block w-full text-left px-3 py-2 text-sm text-scil hover:text-scil-light hover:bg-surface rounded-lg transition-colors"
        >
          Training
        </a>
        <a
          href="/bookings"
          className="block w-full text-left px-3 py-2 text-sm text-scil hover:text-scil-light hover:bg-surface rounded-lg transition-colors"
        >
          Buchungen
        </a>
        <a
          href="/codes"
          className="block w-full text-left px-3 py-2 text-sm text-slate-400 hover:text-slate-200 hover:bg-surface rounded-lg transition-colors"
        >
          Codes
        </a>
        <a
          href="/profile"
          className="block w-full text-left px-3 py-2 text-sm text-slate-400 hover:text-slate-200 hover:bg-surface rounded-lg transition-colors"
        >
          Profil
        </a>
        <button
          onClick={onLogout}
          className="w-full text-left px-3 py-2 text-sm text-slate-400 hover:text-slate-200 hover:bg-surface rounded-lg transition-colors"
        >
          Abmelden
        </button>
      </div>
    </div>
  );
}
