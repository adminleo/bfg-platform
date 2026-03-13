"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface InvitationInfo {
  coach_name: string;
  coach_email: string;
  coachee_email: string;
  has_code: boolean;
  status: string;
}

export default function InvitationPage() {
  const params = useParams();
  const router = useRouter();
  const token = params.token as string;

  const [info, setInfo] = useState<InvitationInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  // Form state
  const [fullName, setFullName] = useState("");
  const [password, setPassword] = useState("");
  const [passwordConfirm, setPasswordConfirm] = useState("");

  useEffect(() => {
    if (!token) return;

    fetch(`${API_URL}/api/v1/invite/${token}`)
      .then(async (res) => {
        if (!res.ok) {
          const data = await res.json().catch(() => ({}));
          throw new Error(data.detail || "Einladung nicht gefunden");
        }
        return res.json();
      })
      .then((data) => setInfo(data))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [token]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (password !== passwordConfirm) {
      setError("Passwoerter stimmen nicht ueberein.");
      return;
    }

    if (password.length < 6) {
      setError("Passwort muss mindestens 6 Zeichen haben.");
      return;
    }

    setSubmitting(true);
    try {
      const res = await fetch(`${API_URL}/api/v1/invite/${token}/accept`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          full_name: fullName,
          password,
        }),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || "Fehler bei der Registrierung");
      }

      const data = await res.json();

      // Auto-login: store JWT and user data
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem(
        "user_data",
        JSON.stringify({
          id: data.user_id,
          email: info?.coachee_email || "",
          full_name: fullName,
          role: "trainee",
        })
      );

      // Redirect to dashboard
      router.push("/dashboard");
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Fehler";
      setError(msg);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
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

  if (error && !info) {
    return (
      <div className="min-h-screen bg-surface-dark flex items-center justify-center p-6">
        <div className="max-w-md w-full bg-surface border border-border rounded-xl p-8 text-center">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-red-500/20 flex items-center justify-center">
            <svg className="w-8 h-8 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <h1 className="text-xl font-bold text-white mb-2">Einladung ungueltig</h1>
          <p className="text-slate-400 text-sm mb-6">{error}</p>
          <button
            onClick={() => router.push("/login")}
            className="px-6 py-2.5 bg-scil hover:bg-scil-dark text-white font-medium rounded-lg transition-colors"
          >
            Zum Login
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-surface-dark flex items-center justify-center p-6">
      <div className="max-w-md w-full bg-surface border border-border rounded-xl p-8">
        {/* Header */}
        <div className="text-center mb-6">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-scil/20 flex items-center justify-center">
            <svg className="w-8 h-8 text-scil" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
          <h1 className="text-xl font-bold text-white mb-1">Einladung zur SCIL-Diagnostik</h1>
          <p className="text-slate-400 text-sm">
            von <span className="text-white font-medium">{info?.coach_name}</span>
          </p>
        </div>

        {info?.has_code && (
          <div className="mb-6 p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-lg text-center">
            <p className="text-emerald-400 text-sm">
              Ein Diagnostik-Code wurde fuer dich reserviert.
            </p>
          </div>
        )}

        {error && (
          <div className="mb-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm">
            {error}
          </div>
        )}

        {/* Registration Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-400 mb-1">E-Mail</label>
            <input
              type="email"
              value={info?.coachee_email || ""}
              disabled
              className="w-full px-3 py-2.5 bg-surface-dark border border-border rounded-lg
                         text-slate-500 cursor-not-allowed"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-400 mb-1">Vollstaendiger Name *</label>
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
              placeholder="Max Mustermann"
              className="w-full px-3 py-2.5 bg-surface-dark border border-border rounded-lg
                         text-white placeholder-slate-500 focus:outline-none focus:border-scil"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-400 mb-1">Passwort *</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={6}
              placeholder="Mindestens 6 Zeichen"
              className="w-full px-3 py-2.5 bg-surface-dark border border-border rounded-lg
                         text-white placeholder-slate-500 focus:outline-none focus:border-scil"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-400 mb-1">Passwort bestaetigen *</label>
            <input
              type="password"
              value={passwordConfirm}
              onChange={(e) => setPasswordConfirm(e.target.value)}
              required
              minLength={6}
              placeholder="Passwort wiederholen"
              className="w-full px-3 py-2.5 bg-surface-dark border border-border rounded-lg
                         text-white placeholder-slate-500 focus:outline-none focus:border-scil"
            />
          </div>

          <button
            type="submit"
            disabled={submitting || !fullName || !password}
            className="w-full py-2.5 bg-scil hover:bg-scil-dark text-white font-medium
                       rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed mt-2"
          >
            {submitting ? "Wird registriert..." : "Einladung annehmen"}
          </button>
        </form>

        <p className="text-center text-xs text-slate-500 mt-4">
          Bereits registriert?{" "}
          <a href="/login" className="text-scil hover:underline">
            Zum Login
          </a>
        </p>
      </div>
    </div>
  );
}
