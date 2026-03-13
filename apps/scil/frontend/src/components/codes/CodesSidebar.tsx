"use client";

import type { DiagnosticCode } from "@/lib/types";

interface CodesSidebarProps {
  codes: DiagnosticCode[];
  onRedeemClick: () => void;
}

export function CodesSidebar({ codes, onRedeemClick }: CodesSidebarProps) {
  const activeCodes = codes.filter((c) => ["emitted", "sold", "activated"].includes(c.status));
  const usedCodes = codes.filter((c) => ["consumed", "expired"].includes(c.status));

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-4">
        <div className="flex items-center gap-2 mb-1">
          <svg className="w-5 h-5 text-scil" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
          </svg>
          <h2 className="text-sm font-semibold text-white">Codes</h2>
        </div>
        <p className="text-xs text-slate-500">Diagnostik-Codes verwalten</p>
      </div>

      {/* Code inventory */}
      <div className="px-4 pb-3">
        <div className="bg-surface rounded-lg p-3 border border-border space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400">Aktive Codes</span>
            <span className="text-sm font-bold text-emerald-400">{activeCodes.length}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400">Verwendete Codes</span>
            <span className="text-sm font-bold text-slate-500">{usedCodes.length}</span>
          </div>
          <div className="flex items-center justify-between pt-1 border-t border-border">
            <span className="text-xs text-slate-400">Gesamt</span>
            <span className="text-sm font-bold text-white">{codes.length}</span>
          </div>
        </div>
      </div>

      {/* Active code status breakdown */}
      {activeCodes.length > 0 && (
        <div className="px-4 pb-3">
          <div className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-2">Aktive Codes</div>
          <div className="space-y-1">
            {activeCodes.slice(0, 8).map((code) => (
              <div key={code.id} className="flex items-center justify-between bg-surface rounded-lg px-2.5 py-1.5 border border-border">
                <code className="text-[10px] text-slate-400 font-mono">
                  {code.token_code.slice(0, 10)}...
                </code>
                <span className={`text-[10px] font-medium ${
                  code.status === "activated" ? "text-scil" :
                  code.status === "emitted" ? "text-emerald-400" :
                  "text-blue-400"
                }`}>
                  {code.status === "activated" ? "Aktiviert" :
                   code.status === "emitted" ? "Verfuegbar" : "Verkauft"}
                </span>
              </div>
            ))}
            {activeCodes.length > 8 && (
              <p className="text-[10px] text-slate-500 text-center py-1">
                +{activeCodes.length - 8} weitere
              </p>
            )}
          </div>
        </div>
      )}

      <div className="flex-1" />

      {/* Redeem button */}
      <div className="p-4 border-t border-border">
        <button
          onClick={onRedeemClick}
          className="w-full px-3 py-2 bg-scil hover:bg-scil-dark text-white text-xs font-medium rounded-lg transition-colors"
        >
          Code einloesen
        </button>
      </div>
    </div>
  );
}
