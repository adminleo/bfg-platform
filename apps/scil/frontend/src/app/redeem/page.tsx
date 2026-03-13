"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { useCodes } from "@/hooks/useCodes";

export default function RedeemPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const { redeemCode, isLoading } = useCodes();
  const [code, setCode] = useState("");
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.replace("/login");
    }
  }, [authLoading, isAuthenticated, router]);

  const handleRedeem = async () => {
    if (!code.trim()) return;
    setMessage(null);

    const result = await redeemCode(code.trim());
    if (result.success) {
      setMessage({ type: "success", text: result.message });
      setCode("");
      // Redirect to dashboard after short delay
      setTimeout(() => router.push("/dashboard"), 2000);
    } else {
      setMessage({ type: "error", text: result.message });
    }
  };

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

  return (
    <div className="min-h-screen bg-surface-dark flex items-center justify-center p-6">
      <div className="max-w-md w-full bg-surface border border-border rounded-xl p-8">
        <h1 className="text-2xl font-bold text-white mb-2 text-center">
          Code einloesen
        </h1>
        <p className="text-slate-400 text-sm text-center mb-8">
          Gib deinen SCIL-Diagnostik-Code ein, um eine Diagnostik freizuschalten.
        </p>

        {message && (
          <div
            className={`mb-4 p-3 rounded-lg text-sm ${
              message.type === "success"
                ? "bg-emerald-500/10 border border-emerald-500/30 text-emerald-400"
                : "bg-red-500/10 border border-red-500/30 text-red-400"
            }`}
          >
            {message.text}
          </div>
        )}

        <div className="space-y-4">
          <input
            type="text"
            value={code}
            onChange={(e) => setCode(e.target.value)}
            placeholder="Diagnostik-Code eingeben..."
            className="w-full px-4 py-3 bg-surface-dark border border-border rounded-lg
                       text-white placeholder-slate-500 focus:outline-none focus:border-scil/50
                       font-mono text-sm"
            onKeyDown={(e) => e.key === "Enter" && handleRedeem()}
          />

          <button
            onClick={handleRedeem}
            disabled={isLoading || !code.trim()}
            className="w-full py-3 bg-scil hover:bg-scil-dark text-white font-medium
                       rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? "Wird eingeloest..." : "Code einloesen"}
          </button>
        </div>

        <div className="mt-6 pt-4 border-t border-border flex justify-between">
          <button
            onClick={() => router.push("/codes")}
            className="text-sm text-slate-400 hover:text-white transition-colors"
          >
            Codes kaufen
          </button>
          <button
            onClick={() => router.push("/dashboard")}
            className="text-sm text-slate-400 hover:text-white transition-colors"
          >
            Zurueck zum Dashboard
          </button>
        </div>
      </div>
    </div>
  );
}
