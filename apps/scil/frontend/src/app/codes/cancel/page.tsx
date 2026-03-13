"use client";

import { useRouter } from "next/navigation";

export default function PurchaseCancelPage() {
  const router = useRouter();

  return (
    <div className="min-h-screen bg-surface-dark flex items-center justify-center p-6">
      <div className="max-w-md w-full bg-surface border border-border rounded-xl p-8 text-center">
        <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-yellow-500/20 flex items-center justify-center">
          <svg className="w-8 h-8 text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        </div>
        <h1 className="text-xl font-bold text-white mb-2">Kauf abgebrochen</h1>
        <p className="text-slate-400 text-sm mb-6">
          Der Kaufvorgang wurde abgebrochen. Es wurde nichts berechnet.
        </p>
        <div className="flex gap-3">
          <button
            onClick={() => router.push("/codes")}
            className="flex-1 py-2.5 bg-scil hover:bg-scil-dark text-white font-medium
                       rounded-lg transition-colors"
          >
            Zurueck zu den Codes
          </button>
          <button
            onClick={() => router.push("/dashboard")}
            className="flex-1 py-2.5 bg-surface-hover hover:bg-surface-light text-slate-300
                       rounded-lg transition-colors border border-border"
          >
            Dashboard
          </button>
        </div>
      </div>
    </div>
  );
}
