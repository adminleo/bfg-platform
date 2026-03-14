"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useCodes } from "@/hooks/useCodes";
import { AppShell } from "@/components/layout/AppShell";
import { CodesSidebar } from "@/components/codes/CodesSidebar";
import type { CodePackage, DiagnosticCode } from "@/lib/types";

const STATUS_LABELS: Record<string, { label: string; color: string }> = {
  emitted: { label: "Verfuegbar", color: "text-emerald-400" },
  sold: { label: "Gekauft", color: "text-blue-400" },
  assigned: { label: "Zugewiesen", color: "text-yellow-400" },
  activated: { label: "Aktiviert", color: "text-scil" },
  consumed: { label: "Verwendet", color: "text-slate-500" },
  expired: { label: "Abgelaufen", color: "text-red-400" },
};

function PackageCard({
  pkg,
  onBuy,
  onDevBuy,
  isLoading,
  isDev,
}: {
  pkg: CodePackage;
  onBuy: () => void;
  onDevBuy: () => void;
  isLoading: boolean;
  isDev: boolean;
}) {
  const unitPrice = (pkg.unit_price_cents / 100).toFixed(2);
  const totalPrice = (pkg.total_price_cents / 100).toFixed(2);

  return (
    <div className="glass-card p-6 flex flex-col">
      <div className="flex-1">
        <div className="flex items-start justify-between mb-3">
          <h3 className="text-lg font-semibold text-slate-900">{pkg.label}</h3>
          {pkg.savings_percent > 0 && (
            <span className="bg-scil/20 text-scil text-xs font-medium px-2 py-1 rounded-full">
              -{pkg.savings_percent}%
            </span>
          )}
        </div>
        <div className="mb-4">
          <span className="text-3xl font-bold text-slate-900 stat-number">{unitPrice} EUR</span>
          <span className="text-slate-500 text-sm ml-1">/ Code</span>
        </div>
        {pkg.quantity > 1 && (
          <p className="text-slate-500 text-sm mb-4">
            {pkg.quantity} Codes = {totalPrice} EUR gesamt
          </p>
        )}
      </div>
      <div className="flex flex-col gap-2">
        <button
          onClick={onBuy}
          disabled={isLoading}
          className="w-full py-2.5 btn-glass text-white font-medium
                     rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? "Wird verarbeitet..." : "Jetzt kaufen"}
        </button>
        {isDev && (
          <button
            onClick={onDevBuy}
            disabled={isLoading}
            className="w-full py-2 btn-ghost text-slate-600
                       text-sm rounded-xl transition-colors
                       disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Dev: Gratis generieren
          </button>
        )}
      </div>
    </div>
  );
}

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
  const router = useRouter();
  const { codes, packages, isLoading, error, purchasePackage, devPurchase, activateCode } = useCodes();
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

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

  const handleDevPurchase = async (packageType: string) => {
    const purchase = await devPurchase(packageType);
    if (purchase) {
      setSuccessMsg("Code generiert und aktiviert! Du kannst jetzt eine Diagnostik starten.");
      setTimeout(() => setSuccessMsg(null), 5000);
    }
  };

  return (
    <AppShell
      leftSidebar={
        <CodesSidebar
          codes={codes}
          onRedeemClick={() => router.push("/redeem")}
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
          <h1 className="text-xl font-bold text-slate-900">SCIL Diagnostik-Codes</h1>
          <p className="text-slate-500 text-sm mt-1">
            Kaufe Codes fuer die SCIL-Wirkungsdiagnostik
          </p>
        </div>

        {/* Package Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 mb-12 animate-fade-in-up">
          {packages.map((pkg, index) => (
            <div key={pkg.type} className={`stagger-${Math.min(index + 1, 6)} animate-fade-in-up`}>
              <PackageCard
                pkg={pkg}
                onBuy={() => purchasePackage(pkg.type)}
                onDevBuy={() => handleDevPurchase(pkg.type)}
                isLoading={isLoading}
                isDev={isDev}
              />
            </div>
          ))}
        </div>

        {/* My Codes */}
        {codes.length > 0 && (
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
        )}
      </div>
    </AppShell>
  );
}
