"use client";

import { useState, useCallback, ReactNode } from "react";

interface NavItem {
  label: string;
  href: string;
  icon: ReactNode;
  active?: boolean;
  accent?: boolean;
}

interface ThreePanelLayoutProps {
  left: ReactNode;
  center: ReactNode;
  right: ReactNode;
  navItems?: NavItem[];
  currentPath?: string;
  rightDefaultOpen?: boolean;
}

export function ThreePanelLayout({ left, center, right, navItems, currentPath, rightDefaultOpen }: ThreePanelLayoutProps) {
  const [leftOpen, setLeftOpen] = useState(true);
  const [rightOpen, setRightOpen] = useState(rightDefaultOpen ?? true);

  const toggleLeft = useCallback(() => setLeftOpen((o) => !o), []);
  const toggleRight = useCallback(() => setRightOpen((o) => !o), []);

  return (
    <div className="flex h-screen overflow-hidden bg-mesh">
      {/* Left Sidebar */}
      <div
        className={`sidebar-transition flex-shrink-0 overflow-hidden ${
          leftOpen ? "w-[260px]" : "w-0"
        }`}
      >
        <div className="w-[260px] h-full overflow-y-auto border-r border-black/[0.06]">{left}</div>
      </div>

      {/* Center + Right wrapper (with top header nav) */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header Navigation Bar */}
        {navItems && navItems.length > 0 && (
          <div className="flex-shrink-0 h-12 glass-subtle border-b border-black/[0.06] flex items-center px-3 gap-1 z-10">
            {/* Left toggle */}
            <button
              onClick={toggleLeft}
              className="p-1.5 rounded-lg hover:bg-black/[0.04] text-slate-400 hover:text-slate-700 transition-all duration-200 mr-1"
              title="Sidebar ein-/ausblenden"
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <rect x="1" y="2" width="4" height="12" rx="1" stroke="currentColor" strokeWidth="1.5" />
                <rect x="7" y="2" width="8" height="12" rx="1" stroke="currentColor" strokeWidth="1.5" />
              </svg>
            </button>

            <div className="w-px h-5 bg-black/[0.08] mr-1" />

            {/* Nav items */}
            {navItems.map((item) => {
              const isActive = currentPath === item.href;
              return (
                <a
                  key={item.href}
                  href={item.href}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200 ${
                    isActive
                      ? "nav-pill-active text-scil"
                      : item.accent
                        ? "text-scil/80 hover:text-scil hover:bg-scil/[0.08]"
                        : "text-slate-500 hover:bg-black/[0.04] hover:text-slate-900"
                  }`}
                >
                  {item.icon}
                  {item.label}
                </a>
              );
            })}

            {/* Spacer + right toggle */}
            <div className="flex-1" />
            <button
              onClick={toggleRight}
              className="p-1.5 rounded-lg hover:bg-black/[0.04] text-slate-400 hover:text-slate-700 transition-all duration-200"
              title="SCIL-Profil ein-/ausblenden"
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <rect x="1" y="2" width="8" height="12" rx="1" stroke="currentColor" strokeWidth="1.5" />
                <rect x="11" y="2" width="4" height="12" rx="1" stroke="currentColor" strokeWidth="1.5" />
              </svg>
            </button>
          </div>
        )}

        {/* Content area */}
        <div className="flex-1 flex min-h-0">
          {/* Center Panel */}
          <div className="flex-1 flex flex-col min-w-0 relative overflow-y-auto">
            {/* Fallback toggle buttons (if no navItems) */}
            {(!navItems || navItems.length === 0) && (
              <>
                <div className="absolute top-3 left-3 z-10 flex gap-1">
                  <button
                    onClick={toggleLeft}
                    className="p-1.5 rounded-lg glass hover:bg-black/[0.06] text-slate-400 hover:text-slate-700 transition-all duration-200"
                    title="Sidebar ein-/ausblenden"
                  >
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                      <rect x="1" y="2" width="4" height="12" rx="1" stroke="currentColor" strokeWidth="1.5" />
                      <rect x="7" y="2" width="8" height="12" rx="1" stroke="currentColor" strokeWidth="1.5" />
                    </svg>
                  </button>
                </div>
                <div className="absolute top-3 right-3 z-10">
                  <button
                    onClick={toggleRight}
                    className="p-1.5 rounded-lg glass hover:bg-black/[0.06] text-slate-400 hover:text-slate-700 transition-all duration-200"
                    title="Profil ein-/ausblenden"
                  >
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                      <rect x="1" y="2" width="8" height="12" rx="1" stroke="currentColor" strokeWidth="1.5" />
                      <rect x="11" y="2" width="4" height="12" rx="1" stroke="currentColor" strokeWidth="1.5" />
                    </svg>
                  </button>
                </div>
              </>
            )}
            {center}
          </div>

          {/* Right Sidebar */}
          <div
            className={`sidebar-transition flex-shrink-0 overflow-hidden ${
              rightOpen ? "w-[340px]" : "w-0"
            }`}
          >
            <div className="w-[340px] h-full overflow-y-auto border-l border-black/[0.06]">{right}</div>
          </div>
        </div>
      </div>
    </div>
  );
}
