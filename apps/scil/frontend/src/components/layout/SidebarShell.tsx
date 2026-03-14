"use client";

import { useState, ReactNode } from "react";

interface SidebarShellProps {
  children: ReactNode;
  userName?: string;
  userEmail?: string;
  onLogout: () => void;
  header?: ReactNode;
}

export function SidebarShell({
  children,
  userName,
  userEmail,
  onLogout,
  header,
}: SidebarShellProps) {
  const [profileOpen, setProfileOpen] = useState(false);

  const initials = (userName || "U")
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);

  return (
    <div className="flex flex-col h-full bg-white/80">
      {/* Optional header slot */}
      {header && (
        <div className="border-b border-black/[0.06]">{header}</div>
      )}

      {/* Page-specific sidebar content */}
      <div className="flex-1 overflow-y-auto">{children}</div>

      {/* Profile Dropdown Footer — shared across all pages */}
      <div className="relative border-t border-black/[0.06]">
        <button
          onClick={() => setProfileOpen(!profileOpen)}
          className="w-full flex items-center gap-3 p-4 hover:bg-black/[0.03] transition-all duration-200"
        >
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-scil/15 to-scil-50 flex items-center justify-center text-xs font-semibold text-scil flex-shrink-0 ring-1 ring-black/[0.06]">
            {initials}
          </div>
          <div className="flex-1 text-left min-w-0">
            <div className="text-sm font-medium text-slate-900 truncate">
              {userName || "Benutzer"}
            </div>
            <div className="text-xs text-slate-500 truncate">
              {userEmail || ""}
            </div>
          </div>
          <svg
            className={`w-4 h-4 text-slate-500 transition-transform duration-200 ${profileOpen ? "rotate-180" : ""}`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
          </svg>
        </button>

        {/* Dropdown menu */}
        {profileOpen && (
          <div className="absolute bottom-full left-0 right-0 mb-1 mx-2 glass-strong rounded-xl shadow-glass-lg py-1 z-50 animate-fade-in-down">
            <a
              href="/profile"
              className="flex items-center gap-2 px-4 py-2.5 text-sm text-slate-600 hover:bg-black/[0.04] hover:text-slate-900 transition-all duration-200 rounded-lg mx-1"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              Profil
            </a>
            <a
              href="/redeem"
              className="flex items-center gap-2 px-4 py-2.5 text-sm text-slate-600 hover:bg-black/[0.04] hover:text-slate-900 transition-all duration-200 rounded-lg mx-1"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
              </svg>
              Code einloesen
            </a>
            <div className="border-t border-black/[0.06] my-1 mx-3" />
            <button
              onClick={() => {
                setProfileOpen(false);
                onLogout();
              }}
              className="w-full flex items-center gap-2 px-4 py-2.5 text-sm text-red-500 hover:bg-red-500/[0.06] transition-all duration-200 rounded-lg mx-1"
              style={{ width: "calc(100% - 8px)" }}
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
