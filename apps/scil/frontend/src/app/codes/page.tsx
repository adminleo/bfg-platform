"use client";

import { useState } from "react";
import { useCodes } from "@/hooks/useCodes";
import { AppShell } from "@/components/layout/AppShell";
import { CodesSidebar } from "@/components/codes/CodesSidebar";
import type { DiagnosticCode } from "@/lib/types";

const STATUS_LABELS: Record<string, { label: string; color: string }> = {
  emitted: { label: "Verfuegbar", color: "text-emerald-400" },
  sold: { label: "Gekauft", color: "text-blue-400" },
  assigned: { label: "Zugewiesen", color: "text-yellow-400" },
  activated: { label: "Aktiviert", color: "text-scil" },
  consumed: { label: "Verwendet", color: "text-slate-500" },
  expired: { label: "Abgelaufen", color: "text-red-400" },
};

function CodeRow({
  code,
  onActivate,
  isLoading,
}: {
  code: DiagnosticCode;
  onActivate: (codeId: string) => void;
  isLoading: boolean;
}) {
  const [revealed, setRevealed] = useState(false);
  const [copied, setCopied] = useState(false);
  const statusInfo = STATUS_LABELS[code.status] || {
    label: code.status,
    color: "text-slate-400",
  };
  const canActivate = code.status === "emitted" || code.status === "sold" || code.status === "assigned";
  const isActivated = code.status === "activated";

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code.token_code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      const textarea = document.createElement("textarea");
      textarea.value = code.token_code;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand("copy");
      document.body.removeChild(textarea);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="py-3 px-4 bg-black/[0.02] border border-black/[0.06] rounded-xl">
      <div className="flex items-center justify-between gap-3">
        {/* Code + copy/reveal */}
        <div className="flex items-center gap-2 flex-1 min-w-0">
          <code className="text-sm text-slate-600 font-mono truncate">
            {revealed ? code.token_code : `${code.token_code.slice(0, 12)}...`}
          </code>
          <button
            onClick={() => setRevealed((r) => !r)}
            className="flex-shrink-0 p-1 rounded hover:bg-black/[0.04] text-slate-400 hover:text-slate-700 transition-colors"
            title={revealed ? "Code verbergen" : "Code anzeigen"}
          >
            {revealed ? (
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21" />
              </svg>
            ) : (
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
            )}
          </button>
          <button
            onClick={handleCopy}
            className="flex-shrink-0 p-1 rounded hover:bg-black/[0.04] text-slate-400 hover:text-slate-700 transition-colors"
            title="Code kopieren"
          >
            {copied ? (
              <svg className="w-4 h-4 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M5 13l4 4L19 7" />
              </svg>
            ) : (
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            )}
          </button>
        </div>

        {/* Status + actions */}
        <div className="flex items-center gap-2 flex-shrink-0">
          <span className="text-xs text-slate-400">
            {new Date(code.created_at).toLocaleDateString("de-DE")}
          </span>
          <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${statusInfo.color} bg-black/[0.03]`}>
            {statusInfo.label}
          </span>

          {/* Activate button for sold/emitted codes */}
          {canActivate && (
            <button
              onClick={() => onActivate(code.id)}
              disabled={isLoading}
              className="px-3 py-1 text-xs font-medium text-white btn-glass rounded-lg transition-all disabled:opacity-50"
            >
              Aktivieren
            </button>
          )}

          {/* Start diagnostic link for activated codes */}
          {isActivated && (
            <a
              href="/dashboard"
              className="px-3 py-1 text-xs font-medium text-white bg-emerald-500/80 hover:bg-emerald-500 rounded-lg transition-all"
            >
              Diagnostik starten
            </a>
          )}
        </div>
      </div>
    </div>
  );
}

export default function CodesPage() {
  const { codes, isLoading, error, redeemCode, activateCode, devPurchase } = useCodes();
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [redeemInput, setRedeemInput] = useState("");
  const [redeemError, setRedeemError] = useState<string | null>(null);
  const [redeemSuccess, setRedeemSuccess] = useState<string | null>(null);

  const isDev = process.env.NODE_ENV === "development" || typeof window !== 'undefined' && window.location.hostname === 'localhost';
  const activeCodes = codes.filter((c) => ["emitted", "sold", "activated"].includes(c.status));
  const usedCodes = codes.filter((c) => ["consumed", "expired"].includes(c.status));

  const handleActivate = async (codeId: string) => {
    const result = await activateCode(codeId);
    if (result.success) {
      setSuccessMsg(result.message);
      setTimeout(() => setSuccessMsg(null), 5000);
    }
  };

  const handleRedeem = async () => {
    const trimmed = redeemInput.trim();
    if (!trimmed) return;

    setRedeemError(null);
    setRedeemSuccess(null);

    const result = await redeemCode(trimmed);
    if (result.success) {
      setRedeemSuccess(result.message || "Code erfolgreich eingeloest!");
      setRedeemInput("");
      setTimeout(() => setRedeemSuccess(null), 5000);
    } else {
      setRedeemError(result.message);
      setTimeout(() => setRedeemError(null), 5000);
    }
  };

  return (
    <AppShell
      leftSidebar={
        <CodesSidebar
          codes={codes}
        />
      }
      rightDefaultOpen={false}
    >
      <div className="w-full px-6 py-6">
        {/* Success message */}
        {successMsg && (
          <div className="mb-6 p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-emerald-400 text-sm animate-fade-in-up flex items-center justify-between">
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>{successMsg}</span>
            </div>
            <a
              href="/dashboard"
              className="ml-4 px-3 py-1.5 text-xs font-medium text-white bg-emerald-500/80 hover:bg-emerald-500 rounded-lg transition-all flex-shrink-0"
            >
              Zur Diagnostik
            </a>
          </div>
        )}

        {error && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-sm animate-fade-in-up">
            {error}
          </div>
        )}

        {/* Page title */}
        <div className="mb-6 animate-fade-in-up">
          <h1 className="text-xl font-bold text-slate-900">Meine Diagnostik-Codes</h1>
          <p className="text-slate-500 text-sm mt-1">
            Verwalte deine Codes fuer die SCIL-Wirkungsdiagnostik
          </p>
        </div>

        {/* Inline redeem form */}
        <div className="glass-card p-6 mb-8 animate-fade-in-up">
          <h2 className="text-lg font-semibold text-slate-900 mb-3">Code einloesen</h2>
          <div className="flex items-center gap-3">
            <input
              type="text"
              value={redeemInput}
              onChange={(e) => setRedeemInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") handleRedeem();
              }}
              placeholder="Code eingeben..."
              className="glass-input flex-1 px-4 py-2.5 text-slate-900 placeholder-slate-400 rounded-xl"
              disabled={isLoading}
            />
            <button
              onClick={handleRedeem}
              disabled={isLoading || !redeemInput.trim()}
              className="px-5 py-2.5 btn-glass text-white font-medium rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? "Wird eingeloest..." : "Einloesen"}
            </button>
          </div>
          {redeemSuccess && (
            <div className="mt-3 p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-emerald-400 text-sm flex items-center gap-2">
              <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>{redeemSuccess}</span>
            </div>
          )}
          {redeemError && (
            <div className="mt-3 p-3 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-sm flex items-center gap-2">
              <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
              <span>{redeemError}</span>
            </div>
          )}
        </div>

        {/* My Codes */}
        {codes.length > 0 ? (
          <div className="animate-fade-in-up">
            <h2 className="text-xl font-semibold text-slate-900 mb-4">Meine Codes</h2>

            {activeCodes.length > 0 && (
              <div className="mb-6">
                <h3 className="text-sm font-medium text-slate-500 mb-2 uppercase tracking-wider">
                  Aktive Codes ({activeCodes.length})
                </h3>
                <div className="space-y-2">
                  {activeCodes.map((code) => (
                    <CodeRow
                      key={code.id}
                      code={code}
                      onActivate={handleActivate}
                      isLoading={isLoading}
                    />
                  ))}
                </div>
              </div>
            )}

            {usedCodes.length > 0 && (
              <div>
                <h3 className="text-sm font-medium text-slate-500 mb-2 uppercase tracking-wider">
                  Verwendete Codes ({usedCodes.length})
                </h3>
                <div className="space-y-2">
                  {usedCodes.map((code) => (
                    <CodeRow
                      key={code.id}
                      code={code}
                      onActivate={handleActivate}
                      isLoading={isLoading}
                    />
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          /* Empty state */
          <div className="glass-card p-8 text-center animate-fade-in-up">
            <svg className="w-12 h-12 text-slate-300 mx-auto mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
            </svg>
            <p className="text-slate-500 mb-3">
              Keine Codes vorhanden. Loese oben einen Code ein oder kaufe neue Codes.
            </p>
            <a
              href="/resources"
              className="inline-block px-5 py-2.5 btn-glass text-white font-medium rounded-xl transition-colors"
            >
              Codes kaufen
            </a>
          </div>
        )}
      </div>
    </AppShell>
  );
}
