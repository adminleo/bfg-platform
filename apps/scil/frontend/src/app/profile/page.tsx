"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { useProfile } from "@/hooks/useProfile";

export default function ProfilePage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const {
    profile,
    coach,
    history,
    isLoading,
    error,
    updateProfile,
    changePassword,
  } = useProfile();

  const [editMode, setEditMode] = useState(false);
  const [fullName, setFullName] = useState("");
  const [bio, setBio] = useState("");
  const [saving, setSaving] = useState(false);

  const [showPassword, setShowPassword] = useState(false);
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [passwordMsg, setPasswordMsg] = useState<string | null>(null);

  // Auth guard
  if (authLoading || isLoading) {
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

  if (!isAuthenticated) {
    router.replace("/login");
    return null;
  }

  const startEdit = () => {
    setFullName(profile?.full_name || "");
    setBio(profile?.bio || "");
    setEditMode(true);
  };

  const handleSave = async () => {
    setSaving(true);
    const ok = await updateProfile({ full_name: fullName, bio });
    setSaving(false);
    if (ok) setEditMode(false);
  };

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    setPasswordMsg(null);
    const ok = await changePassword(currentPassword, newPassword);
    if (ok) {
      setPasswordMsg("Passwort erfolgreich geaendert.");
      setCurrentPassword("");
      setNewPassword("");
      setShowPassword(false);
    }
  };

  return (
    <div className="min-h-screen bg-surface-dark">
      {/* Header */}
      <div className="border-b border-border bg-surface-dark/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-6 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">Mein Profil</h1>
            <p className="text-slate-400 text-sm mt-1">Verwalte deine Kontodaten</p>
          </div>
          <button
            onClick={() => router.push("/dashboard")}
            className="px-4 py-2 bg-surface hover:bg-surface-hover border border-border
                       text-slate-300 rounded-lg transition-colors text-sm"
          >
            Zurueck zum Dashboard
          </button>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-6 py-8 space-y-6">
        {error && (
          <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm">
            {error}
          </div>
        )}

        {/* Profile Card */}
        <div className="bg-surface border border-border rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-white">Persoenliche Daten</h2>
            {!editMode && (
              <button
                onClick={startEdit}
                className="px-3 py-1.5 text-sm text-scil hover:text-scil-light transition-colors"
              >
                Bearbeiten
              </button>
            )}
          </div>

          {editMode ? (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-400 mb-1">Name</label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="w-full px-3 py-2.5 bg-surface-dark border border-border rounded-lg
                             text-white focus:outline-none focus:border-scil"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-400 mb-1">Bio</label>
                <textarea
                  value={bio}
                  onChange={(e) => setBio(e.target.value)}
                  rows={3}
                  placeholder="Erzaehle etwas ueber dich..."
                  className="w-full px-3 py-2.5 bg-surface-dark border border-border rounded-lg
                             text-white placeholder-slate-500 focus:outline-none focus:border-scil resize-none"
                />
              </div>
              <div className="flex gap-3">
                <button
                  onClick={handleSave}
                  disabled={saving}
                  className="px-4 py-2 bg-scil hover:bg-scil-dark text-white text-sm font-medium
                             rounded-lg transition-colors disabled:opacity-50"
                >
                  {saving ? "Wird gespeichert..." : "Speichern"}
                </button>
                <button
                  onClick={() => setEditMode(false)}
                  className="px-4 py-2 bg-surface-hover text-slate-300 text-sm rounded-lg
                             hover:bg-surface-light transition-colors border border-border"
                >
                  Abbrechen
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              <div>
                <span className="text-sm text-slate-500">Name</span>
                <p className="text-white">{profile?.full_name}</p>
              </div>
              <div>
                <span className="text-sm text-slate-500">E-Mail</span>
                <p className="text-white">{profile?.email}</p>
              </div>
              <div>
                <span className="text-sm text-slate-500">Rolle</span>
                <p className="text-white capitalize">{profile?.role}</p>
              </div>
              {profile?.bio && (
                <div>
                  <span className="text-sm text-slate-500">Bio</span>
                  <p className="text-slate-300">{profile.bio}</p>
                </div>
              )}
              <div>
                <span className="text-sm text-slate-500">Mitglied seit</span>
                <p className="text-white">
                  {profile?.created_at
                    ? new Date(profile.created_at).toLocaleDateString("de-DE")
                    : "-"}
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Coach Card */}
        {coach && (
          <div className="bg-surface border border-border rounded-xl p-6">
            <h2 className="text-lg font-semibold text-white mb-4">Mein Coach</h2>
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-full bg-scil/20 flex items-center justify-center text-scil font-bold text-lg">
                {coach.coach_name.charAt(0)}
              </div>
              <div>
                <div className="text-white font-medium">{coach.coach_name}</div>
                <div className="text-sm text-slate-400">{coach.coach_email}</div>
                <div className="text-xs text-slate-500 mt-1">
                  Seit {new Date(coach.assigned_at).toLocaleDateString("de-DE")}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Password Change */}
        <div className="bg-surface border border-border rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-white">Passwort</h2>
            {!showPassword && (
              <button
                onClick={() => setShowPassword(true)}
                className="px-3 py-1.5 text-sm text-scil hover:text-scil-light transition-colors"
              >
                Aendern
              </button>
            )}
          </div>

          {showPassword ? (
            <form onSubmit={handlePasswordChange} className="space-y-4">
              {passwordMsg && (
                <div className="p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-lg text-emerald-400 text-sm">
                  {passwordMsg}
                </div>
              )}
              <div>
                <label className="block text-sm font-medium text-slate-400 mb-1">
                  Aktuelles Passwort
                </label>
                <input
                  type="password"
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                  required
                  className="w-full px-3 py-2.5 bg-surface-dark border border-border rounded-lg
                             text-white focus:outline-none focus:border-scil"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-400 mb-1">
                  Neues Passwort
                </label>
                <input
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  required
                  minLength={6}
                  className="w-full px-3 py-2.5 bg-surface-dark border border-border rounded-lg
                             text-white focus:outline-none focus:border-scil"
                />
              </div>
              <div className="flex gap-3">
                <button
                  type="submit"
                  className="px-4 py-2 bg-scil hover:bg-scil-dark text-white text-sm font-medium
                             rounded-lg transition-colors"
                >
                  Passwort aendern
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowPassword(false);
                    setPasswordMsg(null);
                  }}
                  className="px-4 py-2 bg-surface-hover text-slate-300 text-sm rounded-lg
                             hover:bg-surface-light transition-colors border border-border"
                >
                  Abbrechen
                </button>
              </div>
            </form>
          ) : (
            <p className="text-slate-400 text-sm">••••••••</p>
          )}
        </div>

        {/* Diagnostic History */}
        {history.length > 0 && (
          <div className="bg-surface border border-border rounded-xl p-6">
            <h2 className="text-lg font-semibold text-white mb-4">Diagnostik-Verlauf</h2>
            <div className="space-y-2">
              {history.map((h) => (
                <div
                  key={h.id}
                  className="flex items-center justify-between p-3 bg-surface-dark rounded-lg border border-border"
                >
                  <div>
                    <span className="text-sm text-white">
                      {new Date(h.started_at).toLocaleDateString("de-DE", {
                        day: "2-digit",
                        month: "2-digit",
                        year: "numeric",
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </span>
                    <span className="text-xs text-slate-500 ml-2">
                      {Math.round(h.progress * 100)}%
                    </span>
                  </div>
                  <span
                    className={`text-xs font-medium ${
                      h.status === "completed"
                        ? "text-emerald-400"
                        : h.status === "started"
                        ? "text-scil"
                        : "text-slate-400"
                    }`}
                  >
                    {h.status === "completed"
                      ? "Abgeschlossen"
                      : h.status === "started"
                      ? "In Bearbeitung"
                      : h.status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
