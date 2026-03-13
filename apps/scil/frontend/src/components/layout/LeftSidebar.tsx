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
  userName?: string;
  userEmail?: string;
}

export function LeftSidebar({
  sessions,
  activeSessionId,
  onCreateSession,
  onSelectSession,
  onDeleteSession,
  onLogout,
  isLoading,
  userName,
  userEmail,
}: LeftSidebarProps) {
  const [menuOpenId, setMenuOpenId] = useState<string | null>(null);
  const [profileOpen, setProfileOpen] = useState(false);

  const initials = (userName || "U")
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);

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

      {/* Profile Dropdown Footer */}
      <div className="relative border-t border-border">
        <button
          onClick={() => setProfileOpen(!profileOpen)}
          className="w-full flex items-center gap-3 p-4 hover:bg-surface transition-colors"
        >
          <div className="w-8 h-8 rounded-full bg-surface-hover flex items-center justify-center text-xs font-semibold text-slate-300 flex-shrink-0">
            {initials}
          </div>
          <div className="flex-1 text-left min-w-0">
            <div className="text-sm font-medium text-white truncate">
              {userName || "Benutzer"}
            </div>
            <div className="text-xs text-slate-500 truncate">
              {userEmail || ""}
            </div>
          </div>
          <svg
            className={`w-4 h-4 text-slate-500 transition-transform ${profileOpen ? "rotate-180" : ""}`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
          </svg>
        </button>

        {/* Dropdown menu */}
        {profileOpen && (
          <div className="absolute bottom-full left-0 right-0 mb-1 mx-2 bg-surface border border-border rounded-lg shadow-xl py-1 z-50">
            <a
              href="/profile"
              className="flex items-center gap-2 px-4 py-2.5 text-sm text-slate-300 hover:bg-surface-hover hover:text-white transition-colors"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              Profil
            </a>
            <a
              href="/redeem"
              className="flex items-center gap-2 px-4 py-2.5 text-sm text-slate-300 hover:bg-surface-hover hover:text-white transition-colors"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
              </svg>
              Code einloesen
            </a>
            <div className="border-t border-border my-1" />
            <button
              onClick={() => {
                setProfileOpen(false);
                onLogout();
              }}
              className="w-full flex items-center gap-2 px-4 py-2.5 text-sm text-red-400 hover:bg-surface-hover transition-colors"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              Abmelden
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
