"use client";

import { useState } from "react";
import { useCoachDashboard } from "@/hooks/useCoachDashboard";
import { AppShell } from "@/components/layout/AppShell";
import { CoachSidebar } from "@/components/coach/CoachSidebar";
import type { CoacheeDetail, CodeInventoryItem } from "@/lib/types";

const STATUS_LABELS: Record<string, { label: string; color: string }> = {
  invited: { label: "Eingeladen", color: "text-blue-400" },
  pending: { label: "Ausstehend", color: "text-yellow-400" },
  active: { label: "Aktiv", color: "text-scil" },
  completed: { label: "Abgeschlossen", color: "text-emerald-400" },
  archived: { label: "Archiviert", color: "text-slate-500" },
};

function InviteModal({
  isOpen,
  onClose,
  onInvite,
  codes,
}: {
  isOpen: boolean;
  onClose: () => void;
  onInvite: (email: string, notes?: string, tokenId?: string) => Promise<unknown>;
  codes: CodeInventoryItem[];
}) {
  const [email, setEmail] = useState("");
  const [notes, setNotes] = useState("");
  const [selectedCode, setSelectedCode] = useState("");
  const [sending, setSending] = useState(false);

  if (!isOpen) return null;

  const availableCodes = codes.filter((c) => ["emitted", "sold"].includes(c.status));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSending(true);
    await onInvite(email, notes || undefined, selectedCode || undefined);
    setSending(false);
    setEmail("");
    setNotes("");
    setSelectedCode("");
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="bg-surface border border-border rounded-xl p-6 w-full max-w-md mx-4">
        <h2 className="text-lg font-semibold text-white mb-4">Coachee einladen</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-400 mb-1">E-Mail-Adresse *</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="coachee@example.com"
              className="w-full px-3 py-2.5 bg-surface-dark border border-border rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-scil"
            />
          </div>
          {availableCodes.length > 0 && (
            <div>
              <label className="block text-sm font-medium text-slate-400 mb-1">Diagnostik-Code zuweisen (optional)</label>
              <select
                value={selectedCode}
                onChange={(e) => setSelectedCode(e.target.value)}
                className="w-full px-3 py-2.5 bg-surface-dark border border-border rounded-lg text-white focus:outline-none focus:border-scil"
              >
                <option value="">Keinen Code zuweisen</option>
                {availableCodes.map((c) => (
                  <option key={c.id} value={c.id}>{c.token_code} ({c.tier})</option>
                ))}
              </select>
            </div>
          )}
          <div>
            <label className="block text-sm font-medium text-slate-400 mb-1">Notizen (optional)</label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Anmerkungen zum Coachee..."
              rows={2}
              className="w-full px-3 py-2.5 bg-surface-dark border border-border rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-scil resize-none"
            />
          </div>
          <div className="flex gap-3 pt-2">
            <button type="submit" disabled={sending || !email} className="flex-1 py-2.5 bg-scil hover:bg-scil-dark text-white font-medium rounded-lg transition-colors disabled:opacity-50">
              {sending ? "Wird gesendet..." : "Einladung senden"}
            </button>
            <button type="button" onClick={onClose} className="px-4 py-2.5 bg-surface-hover text-slate-300 rounded-lg hover:bg-surface-light transition-colors border border-border">
              Abbrechen
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function CoacheeDetailPanel({
  detail,
  onClose,
}: {
  detail: CoacheeDetail;
  onClose: () => void;
}) {
  const statusInfo = STATUS_LABELS[detail.status] || { label: detail.status, color: "text-slate-400" };

  return (
    <div className="h-full overflow-y-auto p-4 bg-surface-dark">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">
          {detail.coachee_name || detail.coachee_email}
        </h3>
        <button onClick={onClose} className="text-slate-400 hover:text-white transition-colors">&#x2715;</button>
      </div>

      <div className="space-y-4">
        <div className="flex items-center gap-3">
          <span className="text-sm text-slate-400">Status:</span>
          <span className={`text-sm font-medium ${statusInfo.color}`}>{statusInfo.label}</span>
        </div>
        <div>
          <span className="text-sm text-slate-400">E-Mail:</span>
          <span className="text-sm text-white ml-2">{detail.coachee_email}</span>
        </div>
        {detail.notes && (
          <div>
            <span className="text-sm text-slate-400">Notizen:</span>
            <p className="text-sm text-slate-300 mt-1">{detail.notes}</p>
          </div>
        )}
        {detail.token_code && (
          <div className="flex items-center gap-3">
            <span className="text-sm text-slate-400">Code:</span>
            <code className="text-sm text-slate-300 font-mono">{detail.token_code}</code>
            {detail.token_status && (
              <span className="text-xs px-2 py-0.5 rounded-full bg-surface text-slate-400">{detail.token_status}</span>
            )}
          </div>
        )}

        {detail.diagnostic_runs.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-slate-400 mb-2 uppercase tracking-wider">Diagnostik-Verlauf</h4>
            <div className="space-y-2">
              {detail.diagnostic_runs.map((run) => (
                <div key={run.id} className="flex items-center justify-between p-3 bg-surface rounded-lg border border-border">
                  <div>
                    <span className="text-sm text-white">{new Date(run.started_at).toLocaleDateString("de-DE")}</span>
                    <span className="text-xs text-slate-500 ml-2">{Math.round(run.progress * 100)}%</span>
                  </div>
                  <span className={`text-xs font-medium ${run.status === "completed" ? "text-emerald-400" : run.status === "started" ? "text-scil" : "text-slate-400"}`}>
                    {run.status === "completed" ? "Abgeschlossen" : run.status === "started" ? "In Bearbeitung" : run.status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {detail.latest_polygon && (
          <div>
            <h4 className="text-sm font-medium text-slate-400 mb-2 uppercase tracking-wider">SCIL-Profil</h4>
            <div className="p-4 bg-surface rounded-lg border border-border">
              <div className="grid grid-cols-2 gap-3">
                {Object.entries(detail.latest_polygon.areas || {}).map(([key, area]) => (
                  <div key={key} className="text-center">
                    <div className="text-lg font-bold text-white">{(area as { average: number }).average.toFixed(1)}</div>
                    <div className="text-xs text-slate-400">{(area as { label: string }).label}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default function CoachDashboardPage() {
  const {
    stats, coachees, codes, activity,
    isLoading, error, inviteCoachee, fetchCoacheeDetail,
  } = useCoachDashboard();

  const [showInviteModal, setShowInviteModal] = useState(false);
  const [selectedDetail, setSelectedDetail] = useState<CoacheeDetail | null>(null);
  const [loadingDetail, setLoadingDetail] = useState(false);

  const handleSelectCoachee = async (id: string) => {
    setLoadingDetail(true);
    const detail = await fetchCoacheeDetail(id);
    setSelectedDetail(detail);
    setLoadingDetail(false);
  };

  const rightPanel = selectedDetail ? (
    <CoacheeDetailPanel detail={selectedDetail} onClose={() => setSelectedDetail(null)} />
  ) : loadingDetail ? (
    <div className="h-full flex items-center justify-center bg-surface-dark">
      <div className="flex gap-1">
        <div className="w-2 h-2 rounded-full bg-scil typing-dot" />
        <div className="w-2 h-2 rounded-full bg-scil typing-dot" />
        <div className="w-2 h-2 rounded-full bg-scil typing-dot" />
      </div>
    </div>
  ) : (
    <div className="h-full flex items-center justify-center bg-surface-dark">
      <p className="text-sm text-slate-500">Waehle einen Coachee aus</p>
    </div>
  );

  return (
    <>
      <AppShell
        leftSidebar={
          <CoachSidebar
            stats={stats}
            coachees={coachees}
            selectedId={selectedDetail?.id || null}
            onSelectCoachee={handleSelectCoachee}
            onInvite={() => setShowInviteModal(true)}
          />
        }
        rightSidebar={rightPanel}
        rightDefaultOpen={true}
      >
        <div className="p-6 max-w-5xl mx-auto">
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
            <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm">
              {error}
            </div>
          )}

          {/* Stats Cards */}
          {stats && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
              <div className="bg-surface border border-border rounded-xl p-5">
                <div className="text-3xl font-bold text-white mb-1">{stats.total_coachees}</div>
                <div className="text-sm text-slate-400">Coachees</div>
              </div>
              <div className="bg-surface border border-border rounded-xl p-5">
                <div className="text-3xl font-bold text-scil mb-1">{stats.active_diagnostics}</div>
                <div className="text-sm text-slate-400">Aktive Diagnostiken</div>
              </div>
              <div className="bg-surface border border-border rounded-xl p-5">
                <div className="text-3xl font-bold text-emerald-400 mb-1">{stats.codes_available}</div>
                <div className="text-sm text-slate-400">Codes verfuegbar</div>
              </div>
              <div className="bg-surface border border-border rounded-xl p-5">
                <div className="text-3xl font-bold text-blue-400 mb-1">{stats.completed_diagnostics}</div>
                <div className="text-sm text-slate-400">Abgeschlossen</div>
              </div>
            </div>
          )}

          {/* Coachee List (main content) */}
          <div>
            <h2 className="text-lg font-semibold text-white mb-4">Meine Coachees</h2>
            {coachees.length === 0 ? (
              <div className="bg-surface border border-border rounded-xl p-8 text-center">
                <p className="text-slate-400 mb-4">Du hast noch keine Coachees eingeladen.</p>
                <button
                  onClick={() => setShowInviteModal(true)}
                  className="px-4 py-2 bg-scil hover:bg-scil-dark text-white text-sm font-medium rounded-lg transition-colors"
                >
                  Ersten Coachee einladen
                </button>
              </div>
            ) : (
              <div className="space-y-2">
                {coachees.map((c) => {
                  const statusInfo = STATUS_LABELS[c.status] || { label: c.status, color: "text-slate-400" };
                  const isSelected = selectedDetail?.id === c.id;
                  return (
                    <div
                      key={c.id}
                      onClick={() => handleSelectCoachee(c.id)}
                      className={`flex items-center justify-between p-4 rounded-xl border cursor-pointer transition-colors ${
                        isSelected ? "bg-scil/10 border-scil/30" : "bg-surface border-border hover:bg-surface-hover"
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-surface-dark flex items-center justify-center text-slate-400 text-sm font-medium">
                          {(c.coachee_name || c.coachee_email).charAt(0).toUpperCase()}
                        </div>
                        <div>
                          <div className="text-sm font-medium text-white">{c.coachee_name || c.coachee_email}</div>
                          {c.coachee_name && <div className="text-xs text-slate-500">{c.coachee_email}</div>}
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        {c.has_diagnostic && (
                          <span className="text-xs px-2 py-0.5 rounded-full bg-scil/10 text-scil">Diagnostik</span>
                        )}
                        <span className={`text-xs font-medium ${statusInfo.color}`}>{statusInfo.label}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Recent Activity */}
          {activity.length > 0 && (
            <div className="mt-8">
              <h3 className="text-sm font-medium text-slate-400 mb-3 uppercase tracking-wider">Letzte Aktivitaet</h3>
              <div className="space-y-2">
                {activity.slice(0, 5).map((a, idx) => (
                  <div key={idx} className="p-3 bg-surface border border-border rounded-lg">
                    <p className="text-sm text-slate-300">{a.description}</p>
                    <p className="text-xs text-slate-500 mt-1">
                      {new Date(a.timestamp).toLocaleDateString("de-DE", { day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit" })}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </AppShell>

      {/* Invite Modal */}
      <InviteModal
        isOpen={showInviteModal}
        onClose={() => setShowInviteModal(false)}
        onInvite={inviteCoachee}
        codes={codes}
      />
    </>
  );
}
