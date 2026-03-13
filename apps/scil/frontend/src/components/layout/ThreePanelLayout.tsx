"use client";

import { useState, useCallback, ReactNode } from "react";

interface ThreePanelLayoutProps {
  left: ReactNode;
  center: ReactNode;
  right: ReactNode;
}

export function ThreePanelLayout({ left, center, right }: ThreePanelLayoutProps) {
  const [leftOpen, setLeftOpen] = useState(true);
  const [rightOpen, setRightOpen] = useState(true);

  const toggleLeft = useCallback(() => setLeftOpen((o) => !o), []);
  const toggleRight = useCallback(() => setRightOpen((o) => !o), []);

  return (
    <div className="flex h-screen overflow-hidden bg-surface-dark">
      {/* Left Sidebar */}
      <div
        className={`sidebar-transition flex-shrink-0 border-r border-border overflow-hidden ${
          leftOpen ? "w-[260px]" : "w-0"
        }`}
      >
        <div className="w-[260px] h-full overflow-y-auto">{left}</div>
      </div>

      {/* Center Panel */}
      <div className="flex-1 flex flex-col min-w-0 relative">
        {/* Toggle buttons */}
        <div className="absolute top-3 left-3 z-10 flex gap-1">
          <button
            onClick={toggleLeft}
            className="p-1.5 rounded-md bg-surface hover:bg-surface-hover text-slate-400 hover:text-slate-200 transition-colors"
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
            className="p-1.5 rounded-md bg-surface hover:bg-surface-hover text-slate-400 hover:text-slate-200 transition-colors"
            title="Profil ein-/ausblenden"
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <rect x="1" y="2" width="8" height="12" rx="1" stroke="currentColor" strokeWidth="1.5" />
              <rect x="11" y="2" width="4" height="12" rx="1" stroke="currentColor" strokeWidth="1.5" />
            </svg>
          </button>
        </div>

        {center}
      </div>

      {/* Right Sidebar */}
      <div
        className={`sidebar-transition flex-shrink-0 border-l border-border overflow-hidden ${
          rightOpen ? "w-[340px]" : "w-0"
        }`}
      >
        <div className="w-[340px] h-full overflow-y-auto">{right}</div>
      </div>
    </div>
  );
}
