"use client";

import { useState } from "react";
import { useProfile } from "@/hooks/useProfile";
import { AppShell } from "@/components/layout/AppShell";

export default function ProfilePage() {
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

  // Profile sidebar — simple section navigation
  const profileSidebar = (
    <div className="flex flex-col h-full">
      <div className="p-4">
        <div className="flex items-center gap-2 mb-1">
          <svg className="w-5 h-5 text-scil" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
          <h2 className="text-sm font-semibold text-white">Profil</h2>
        </div>
        <p className="text-xs text-slate-500">Kontodaten verwalten</p>
      </div>

      <nav className="px-4 space-y-0.5">
        <a href="#personal" className="flex items-center gap-2 px-3 py-2 text-sm text-slate-300 hover:bg-surface hover:text-white rounded-lg transition-colors">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
          Persoenliche Daten
        </a>
        {coach && (
          <a href="#coach" className="flex items-center gap-2 px-3 py-2 text-sm text-slate-300 hover:bg-surface hover:text-white rounded-lg transition-colors">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            Mein Coach
          </a>
        )}
        <a href="#password" className="flex items-center gap-2 px-3 py-2 text-sm text-slate-300 hover:bg-surface hover:text-white rounded-lg transition-colors">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
          </svg>
          Passwort
        </a>
        {history.length > 0 && (
          <a href="#history" className="flex items-center gap-2 px-3 py-2 text-sm text-slate-300 hover:bg-surface hover:text-white rounded-lg transition-colors">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            Diagnostik-Verlauf
          </a>
        )}
      </nav>
    </div>
  );

  return (
    <AppShell
      leftSidebar={profileSidebar}
      rightDefaultOpen={false}
    >
      <div className="max-w-3xl mx-auto px-6 py-6 space-y-6">
        {isLoading && (
          <div className="flex items-center justify-center py-12">
            <div className="flex gap-1">
              <div className="w-2 h-2 rounded-full bg-scil typing-dot" />
              <div className="w-2 h-2 rounded-full bg-scil typing-dot" />
              <div className="w-2 h-2 rounded-full bg-scil typing-dot" />
            </div>
          </div>
        )}

        {error && (
          <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm">
            {error}
          </div>
        )}

        {/* Profile Card */}
        <div id="personal" className="bg-surface border border-border rounded-xl p-6">
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
          <div id="coach" className="bg-surface border border-border rounded-xl p-6">
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
        <div id="password" className="bg-surface border border-border rounded-xl p-6">
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
            <p className="text-slate-400 text-sm">&bull;&bull;&bull;&bull;&bull;&bull;&bull;&bull;</p>
          )}
        </div>

        {/* Diagnostic History */}
        {history.length > 0 && (
          <div id="history" className="bg-surface border border-border rounded-xl p-6">
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
    </AppShell>
  );
}
