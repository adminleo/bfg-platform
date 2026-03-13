"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { useCodes } from "@/hooks/useCodes";
import type { CodePackage, DiagnosticCode } from "@/lib/types";

const STATUS_LABELS: Record<string, { label: string; color: string }> = {
  emitted: { label: "Verfuegbar", color: "text-emerald-400" },
  sold: { label: "Verkauft", color: "text-blue-400" },
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
    <div className="bg-surface border border-border rounded-xl p-6 flex flex-col">
      <div className="flex-1">
        <div className="flex items-start justify-between mb-3">
          <h3 className="text-lg font-semibold text-white">{pkg.label}</h3>
          {pkg.savings_percent > 0 && (
            <span className="bg-scil/20 text-scil text-xs font-medium px-2 py-1 rounded-full">
              -{pkg.savings_percent}%
            </span>
          )}
        </div>
        <div className="mb-4">
          <span className="text-3xl font-bold text-white">{unitPrice} EUR</span>
          <span className="text-slate-400 text-sm ml-1">/ Code</span>
        </div>
        {pkg.quantity > 1 && (
          <p className="text-slate-400 text-sm mb-4">
            {pkg.quantity} Codes = {totalPrice} EUR gesamt
          </p>
        )}
      </div>
      <div className="flex flex-col gap-2">
        <button
          onClick={onBuy}
          disabled={isLoading}
          className="w-full py-2.5 bg-scil hover:bg-scil-dark text-white font-medium
                     rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? "Wird verarbeitet..." : "Jetzt kaufen"}
        </button>
        {isDev && (
          <button
            onClick={onDevBuy}
            disabled={isLoading}
            className="w-full py-2 bg-surface-hover hover:bg-surface-light text-slate-300
                       text-sm rounded-lg transition-colors border border-border
                       disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Dev: Gratis generieren
          </button>
        )}
      </div>
    </div>
  );
}

function CodeRow({ code }: { code: DiagnosticCode }) {
  const statusInfo = STATUS_LABELS[code.status] || {
    label: code.status,
    color: "text-slate-400",
  };
  const isUsable = code.status === "activated" || code.status === "emitted" || code.status === "sold";

  return (
    <div className="flex items-center justify-between py-3 px-4 bg-surface rounded-lg border border-border">
      <div className="flex-1">
        <code className="text-sm text-slate-300 font-mono">
          {code.token_code.slice(0, 12)}...
        </code>
        <span className="text-xs text-slate-500 ml-3">
          {new Date(code.created_at).toLocaleDateString("de-DE")}
        </span>
      </div>
      <span className={`text-sm font-medium ${statusInfo.color}`}>
        {isUsable && "\u25CF "}
        {statusInfo.label}
      </span>
    </div>
  );
}

export default function CodesPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const { codes, packages, isLoading, error, purchasePackage, devPurchase } = useCodes();

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.replace("/login");
    }
  }, [authLoading, isAuthenticated, router]);

  if (authLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-surface-dark">
        <div className="flex gap-1">
          <div className="w-2 h-2 rounded-full bg-scil typing-dot" />
          <div className="w-2 h-2 rounded-full bg-scil typing-dot" />
          <div className="w-2 h-2 rounded-full bg-scil typing-dot" />
        </div>
      </div>
    );
  }

  if (!isAuthenticated) return null;

  const isDev = process.env.NODE_ENV === "development" || typeof window !== 'undefined' && window.location.hostname === 'localhost';
  const activeCodes = codes.filter((c) => ["emitted", "sold", "activated"].includes(c.status));
  const usedCodes = codes.filter((c) => ["consumed", "expired"].includes(c.status));

  return (
    <div className="min-h-screen bg-surface-dark">
      {/* Header */}
      <div className="border-b border-border bg-surface-dark/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">SCIL Diagnostik-Codes</h1>
            <p className="text-slate-400 text-sm mt-1">
              Kaufe Codes fuer die SCIL-Wirkungsdiagnostik
            </p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => router.push("/redeem")}
              className="px-4 py-2 bg-surface hover:bg-surface-hover border border-border
                         text-slate-300 rounded-lg transition-colors text-sm"
            >
              Code einloesen
            </button>
            <button
              onClick={() => router.push("/dashboard")}
              className="px-4 py-2 bg-surface hover:bg-surface-hover border border-border
                         text-slate-300 rounded-lg transition-colors text-sm"
            >
              Zurueck zum Dashboard
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-6 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm">
            {error}
          </div>
        )}

        {/* Package Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4 mb-12">
          {packages.map((pkg) => (
            <PackageCard
              key={pkg.type}
              pkg={pkg}
              onBuy={() => purchasePackage(pkg.type)}
              onDevBuy={() => devPurchase(pkg.type)}
              isLoading={isLoading}
              isDev={isDev}
            />
          ))}
        </div>

        {/* My Codes */}
        {codes.length > 0 && (
          <div>
            <h2 className="text-xl font-semibold text-white mb-4">Meine Codes</h2>

            {activeCodes.length > 0 && (
              <div className="mb-6">
                <h3 className="text-sm font-medium text-slate-400 mb-2 uppercase tracking-wider">
                  Aktive Codes ({activeCodes.length})
                </h3>
                <div className="space-y-2">
                  {activeCodes.map((code) => (
                    <CodeRow key={code.id} code={code} />
                  ))}
                </div>
              </div>
            )}

            {usedCodes.length > 0 && (
              <div>
                <h3 className="text-sm font-medium text-slate-400 mb-2 uppercase tracking-wider">
                  Verwendete Codes ({usedCodes.length})
                </h3>
                <div className="space-y-2">
                  {usedCodes.map((code) => (
                    <CodeRow key={code.id} code={code} />
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
