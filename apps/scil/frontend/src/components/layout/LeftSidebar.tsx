"use client";

import { useState } from "react";
import type { Session } from "@/lib/types";

interface LeftSidebarProps {
  sessions: Session[];
  activeSessionId: string | null;
  onCreateSession: () => void;
  onSelectSession: (id: string) => void;
  onDeleteSession: (id: string) => void;
  isLoading: boolean;
}

export function LeftSidebar({
  sessions,
  activeSessionId,
  onCreateSession,
  onSelectSession,
  onDeleteSession,
  isLoading,
}: LeftSidebarProps) {
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
      session.status === "completed" ? "\u2713" :
      session.status === "in_progress" ? "\u25CF" : "\u25CB";
    const statusColor =
      session.status === "completed" ? "text-green-600" :
      session.status === "in_progress" ? "text-scil" : "text-slate-500";

    return (
      <div
        key={session.id}
        className={`group flex items-center gap-2 px-3 py-2 rounded-xl cursor-pointer transition-all duration-200 ${
          isActive
            ? "bg-black/[0.05] text-slate-900"
            : "text-slate-500 hover:bg-black/[0.03] hover:text-slate-900"
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
          &#x22EF;
        </button>
        {menuOpenId === session.id && (
          <div className="absolute right-2 mt-16 glass-strong rounded-xl shadow-glass py-1 z-50 animate-fade-in">
            <button
              className="block w-full text-left px-4 py-2 text-sm text-red-400 hover:bg-black/[0.04] rounded-lg mx-0.5"
              style={{ width: "calc(100% - 4px)" }}
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
        <div className="px-3 py-1 text-xs font-medium text-slate-400 uppercase tracking-wider">
          {label}
        </div>
        {items.map(renderSession)}
      </div>
    );
  };

  return (
    <div className="flex flex-col h-full">
      {/* New Diagnostic Button */}
      <div className="p-4">
        <button
          onClick={onCreateSession}
          disabled={isLoading}
          className="w-full flex items-center justify-center gap-2 px-4 py-2.5 btn-glass text-white rounded-xl font-medium transition-all disabled:opacity-50"
        >
          <span className="text-lg">+</span>
          <span>Neue Diagnostik</span>
        </button>
      </div>

      {/* Session List */}
      <div className="flex-1 overflow-y-auto p-2">
        {sessions.length === 0 ? (
          <div className="text-center text-slate-400 text-sm mt-8 px-4">
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
    </div>
  );
}
