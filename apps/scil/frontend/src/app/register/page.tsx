"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";

export default function RegisterPage() {
  const router = useRouter();
  const { register, error } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    const success = await register(email, password, fullName);
    setIsLoading(false);
    if (success) {
      router.push("/dashboard");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-surface-dark p-4">
      <div className="w-full max-w-sm">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-scil to-scil-dark flex items-center justify-center shadow-glow">
              <span className="text-white text-lg font-bold">S</span>
            </div>
            <span className="text-xl font-bold text-slate-900 tracking-tight">S.C.I.L. Profile</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-900">Registrieren</h1>
          <p className="text-slate-600 text-sm mt-1">SCIL Profile Konto erstellen</p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm text-slate-600 mb-1">Name</label>
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="w-full px-4 py-3 bg-surface border border-border rounded-xl text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-scil/50 focus:border-scil"
              placeholder="Vorname Nachname"
              required
            />
          </div>
          <div>
            <label className="block text-sm text-slate-600 mb-1">E-Mail</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-3 bg-surface border border-border rounded-xl text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-scil/50 focus:border-scil"
              placeholder="deine@email.de"
              required
            />
          </div>
          <div>
            <label className="block text-sm text-slate-600 mb-1">Passwort</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 bg-surface border border-border rounded-xl text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-scil/50 focus:border-scil"
              placeholder="Mindestens 8 Zeichen"
              minLength={8}
              required
            />
          </div>

          {error && (
            <div className="text-red-600 text-sm bg-red-400/10 border border-red-400/20 rounded-lg px-3 py-2">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-3 bg-scil hover:bg-scil-dark text-white rounded-xl font-medium transition-colors disabled:opacity-50"
          >
            {isLoading ? "Registrieren..." : "Konto erstellen"}
          </button>
        </form>

        <div className="text-center mt-6">
          <span className="text-slate-500 text-sm">Bereits ein Konto? </span>
          <a
            href="/login"
            className="text-scil hover:text-scil-light text-sm font-medium"
          >
            Anmelden
          </a>
        </div>
      </div>
    </div>
  );
}
