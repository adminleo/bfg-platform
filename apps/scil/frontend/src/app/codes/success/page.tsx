"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { useCodes } from "@/hooks/useCodes";
import type { Purchase } from "@/lib/types";

export default function PurchaseSuccessPage() {
  return (
    <Suspense
      fallback={
        <div className="flex items-center justify-center min-h-screen bg-surface-dark">
          <div className="flex gap-1">
            <div className="w-2 h-2 rounded-full bg-scil typing-dot" />
            <div className="w-2 h-2 rounded-full bg-scil typing-dot" />
            <div className="w-2 h-2 rounded-full bg-scil typing-dot" />
          </div>
        </div>
      }
    >
      <PurchaseSuccessContent />
    </Suspense>
  );
}

function PurchaseSuccessContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const { getPurchase } = useCodes();
  const [purchase, setPurchase] = useState<Purchase | null>(null);
  const [isPolling, setIsPolling] = useState(true);

  const purchaseId = searchParams.get("purchase_id");

  // Poll for purchase completion
  useEffect(() => {
    if (!purchaseId || !isAuthenticated) return;

    let attempts = 0;
    const maxAttempts = 30;

    const poll = async () => {
      const data = await getPurchase(purchaseId);
      if (data) {
        setPurchase(data);
        if (data.status === "completed" || data.status === "failed") {
          setIsPolling(false);
          return;
        }
      }
      attempts++;
      if (attempts >= maxAttempts) {
        setIsPolling(false);
        return;
      }
      setTimeout(poll, 2000);
    };

    poll();
  }, [purchaseId, isAuthenticated, getPurchase]);

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

  return (
    <div className="min-h-screen bg-surface-dark flex items-center justify-center p-6">
      <div className="max-w-lg w-full bg-surface border border-border rounded-xl p-8 text-center">
        {isPolling ? (
          <>
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-scil/20 flex items-center justify-center">
              <div className="flex gap-1">
                <div className="w-2 h-2 rounded-full bg-scil typing-dot" />
                <div className="w-2 h-2 rounded-full bg-scil typing-dot" />
                <div className="w-2 h-2 rounded-full bg-scil typing-dot" />
              </div>
            </div>
            <h1 className="text-xl font-bold text-white mb-2">Zahlung wird verarbeitet...</h1>
            <p className="text-slate-400 text-sm">
              Deine Codes werden generiert. Bitte warte einen Moment.
            </p>
          </>
        ) : purchase?.status === "completed" ? (
          <>
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-emerald-500/20 flex items-center justify-center">
              <svg className="w-8 h-8 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h1 className="text-xl font-bold text-white mb-2">Kauf erfolgreich!</h1>
            <p className="text-slate-400 text-sm mb-6">
              {purchase.quantity} Diagnostik-Code{purchase.quantity > 1 ? "s" : ""} wurden generiert.
            </p>

            {purchase.codes.length > 0 && (
              <div className="mb-6 text-left">
                <h3 className="text-sm font-medium text-slate-400 mb-2">Deine Codes:</h3>
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {purchase.codes.map((code) => (
                    <div
                      key={code.id}
                      className="flex items-center justify-between p-3 bg-surface-dark rounded-lg border border-border"
                    >
                      <code className="text-sm text-slate-300 font-mono">
                        {code.token_code.slice(0, 16)}...
                      </code>
                      <span className="text-xs text-emerald-400">Bereit</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="flex gap-3">
              <button
                onClick={() => router.push("/redeem")}
                className="flex-1 py-2.5 bg-scil hover:bg-scil-dark text-white font-medium
                           rounded-lg transition-colors"
              >
                Code einloesen
              </button>
              <button
                onClick={() => router.push("/codes")}
                className="flex-1 py-2.5 bg-surface-hover hover:bg-surface-light text-slate-300
                           rounded-lg transition-colors border border-border"
              >
                Alle Codes
              </button>
            </div>
          </>
        ) : (
          <>
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-red-500/20 flex items-center justify-center">
              <svg className="w-8 h-8 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <h1 className="text-xl font-bold text-white mb-2">Zahlung fehlgeschlagen</h1>
            <p className="text-slate-400 text-sm mb-6">
              Es gab ein Problem bei der Verarbeitung. Bitte versuche es erneut.
            </p>
            <button
              onClick={() => router.push("/codes")}
              className="w-full py-2.5 bg-scil hover:bg-scil-dark text-white font-medium
                         rounded-lg transition-colors"
            >
              Zurueck zu den Codes
            </button>
          </>
        )}
      </div>
    </div>
  );
}
