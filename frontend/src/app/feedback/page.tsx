"use client";

import { useState } from "react";
import { JohariWindow } from "@/components/diagnostics/JohariWindow";
import { PolygonOverlay } from "@/components/diagnostics/PolygonOverlay";

// Demo data
const DEMO_JOHARI = {
  public: ["analytical_thinking", "clarity", "strategic_thinking"],
  blind_spot: ["empathy", "storytelling"],
  hidden: ["presence", "team_leadership"],
  unknown: ["persuasion"],
};

const DEMO_SELF_SCORES = {
  sensus: { inner_presence: 7.2, conviction: 6.8, moment_focus: 7.5, emotionality: 5.9 },
  corpus: { appearance: 6.5, gesture: 5.8, facial_expression: 7.1, spatial_presence: 7.3 },
  intellektus: { analytics: 8.1, goal_orientation: 7.8, structure: 8.4, objectivity: 7.6 },
  lingua: { voice: 6.9, articulation: 7.3, eloquence: 7.0, imagery: 6.2 },
};

const DEMO_OTHERS_SCORES = {
  sensus: { inner_presence: 6.5, conviction: 7.5, moment_focus: 6.8, emotionality: 7.2 },
  corpus: { appearance: 7.0, gesture: 6.2, facial_expression: 6.5, spatial_presence: 5.8 },
  intellektus: { analytics: 8.3, goal_orientation: 7.5, structure: 8.0, objectivity: 7.8 },
  lingua: { voice: 7.5, articulation: 7.0, eloquence: 6.5, imagery: 6.8 },
};

const DEMO_ROUNDS = [
  {
    id: "1",
    title: "Q1 2025 — Führungsfeedback",
    status: "completed",
    totalRaters: 8,
    completedRaters: 8,
    date: "15.01.2025",
  },
  {
    id: "2",
    title: "Projektfeedback Alpha-Team",
    status: "active",
    totalRaters: 6,
    completedRaters: 3,
    date: "10.02.2025",
  },
];

const PERSPECTIVES = [
  { key: "self", label: "Selbstbild", icon: "🎯", min: 1 },
  { key: "supervisor", label: "Vorgesetzte", icon: "👔", min: 1 },
  { key: "peer", label: "Peers", icon: "🤝", min: 3 },
  { key: "report", label: "Teammitglieder", icon: "👥", min: 3 },
  { key: "external", label: "Externe", icon: "🌐", min: 2 },
];

type Tab = "overview" | "results" | "new";

export default function FeedbackPage() {
  const [activeTab, setActiveTab] = useState<Tab>("overview");

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gr8-navy mb-2">360° Feedback</h1>
      <p className="text-slate-500 mb-8">
        KI-geführtes Multi-Rater-Feedback mit Johari-Window-Analyse und SCIL-Mapping.
      </p>

      {/* Tabs */}
      <div className="flex gap-1 bg-slate-100 rounded-xl p-1 mb-8 w-fit">
        {[
          { key: "overview" as Tab, label: "Übersicht" },
          { key: "results" as Tab, label: "Ergebnisse" },
          { key: "new" as Tab, label: "+ Neue Runde" },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === tab.key
                ? "bg-white text-gr8-navy shadow-sm"
                : "text-slate-500 hover:text-slate-700"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Overview Tab */}
      {activeTab === "overview" && (
        <div className="space-y-6">
          {/* Info Banner */}
          <div className="bg-gradient-to-r from-gr8-navy to-gr8-purple rounded-2xl p-6 text-white">
            <h2 className="font-semibold mb-2 text-lg">Konversationelles 360° Feedback</h2>
            <p className="text-sm text-white/80">
              Unser KI-Agent führt Feedback-Geber durch ein natürliches Gespräch statt starrer Fragebögen.
              Das Ergebnis: tiefere Einblicke, höhere Abschlussraten und anonymisierte SCIL-Scores.
            </p>
            <div className="flex gap-4 mt-4">
              {["STAR-Methodik", "DSGVO-konform", "Min. 3 Rater/Gruppe"].map((tag) => (
                <span key={tag} className="px-2.5 py-1 bg-white/10 rounded-lg text-xs">{tag}</span>
              ))}
            </div>
          </div>

          {/* Active Rounds */}
          <div>
            <h3 className="text-lg font-semibold text-gr8-navy mb-4">Meine Feedback-Runden</h3>
            <div className="space-y-3">
              {DEMO_ROUNDS.map((round) => (
                <div key={round.id} className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 flex items-center justify-between">
                  <div>
                    <h4 className="font-semibold text-gr8-navy">{round.title}</h4>
                    <p className="text-sm text-slate-500">{round.date}</p>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <p className="text-sm font-medium text-slate-700">
                        {round.completedRaters}/{round.totalRaters} Rater
                      </p>
                      <div className="w-24 h-1.5 bg-slate-200 rounded-full mt-1">
                        <div
                          className="h-full bg-gr8-neon rounded-full transition-all"
                          style={{ width: `${(round.completedRaters / round.totalRaters) * 100}%` }}
                        />
                      </div>
                    </div>
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-medium ${
                        round.status === "completed"
                          ? "bg-emerald-50 text-emerald-700"
                          : "bg-amber-50 text-amber-700"
                      }`}
                    >
                      {round.status === "completed" ? "Abgeschlossen" : "Aktiv"}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 5 Perspectives */}
          <div>
            <h3 className="text-lg font-semibold text-gr8-navy mb-4">5 Perspektiven</h3>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
              {PERSPECTIVES.map((p) => (
                <div key={p.key} className="bg-white rounded-xl border border-slate-200 shadow-sm p-4 text-center">
                  <span className="text-2xl">{p.icon}</span>
                  <h4 className="font-medium text-sm text-gr8-navy mt-2">{p.label}</h4>
                  <p className="text-[11px] text-slate-400 mt-1">Min. {p.min} Rater</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Results Tab */}
      {activeTab === "results" && (
        <div className="space-y-8">
          {/* Johari Window */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
            <JohariWindow data={DEMO_JOHARI} />
          </div>

          {/* SCIL Polygon Overlay */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
            <h3 className="text-lg font-semibold text-gr8-navy mb-4 text-center">SCIL-Profil: Selbstbild vs. Fremdbild</h3>
            <PolygonOverlay selfScores={DEMO_SELF_SCORES} othersScores={DEMO_OTHERS_SCORES} size={450} />
          </div>

          {/* Competency Heatmap */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
            <h3 className="text-lg font-semibold text-gr8-navy mb-4">Kompetenz-Übersicht nach Perspektive</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-200">
                    <th className="text-left py-2 text-slate-500 font-medium">Kompetenz</th>
                    <th className="text-center py-2 text-slate-500 font-medium">Selbst</th>
                    <th className="text-center py-2 text-slate-500 font-medium">Vorgesetzte</th>
                    <th className="text-center py-2 text-slate-500 font-medium">Peers</th>
                    <th className="text-center py-2 text-slate-500 font-medium">Team</th>
                    <th className="text-center py-2 text-slate-500 font-medium">Gesamt</th>
                  </tr>
                </thead>
                <tbody>
                  {[
                    { name: "Überzeugungskraft", self: 6.5, sup: 7.2, peer: 7.0, team: 6.8, total: 6.9 },
                    { name: "Analytisches Denken", self: 8.5, sup: 8.3, peer: 8.1, team: 8.0, total: 8.2 },
                    { name: "Empathie", self: 5.8, sup: 7.0, peer: 7.2, team: 7.5, total: 6.9 },
                    { name: "Präsenz", self: 7.5, sup: 6.0, peer: 5.8, team: 6.2, total: 6.4 },
                    { name: "Strategisches Denken", self: 7.8, sup: 7.5, peer: 7.6, team: 7.2, total: 7.5 },
                    { name: "Storytelling", self: 6.0, sup: 7.0, peer: 7.2, team: 6.5, total: 6.7 },
                    { name: "Teamführung", self: 7.0, sup: 6.2, peer: 6.0, team: 5.8, total: 6.3 },
                    { name: "Klarheit", self: 8.0, sup: 8.0, peer: 7.8, team: 7.5, total: 7.8 },
                  ].map((row) => (
                    <tr key={row.name} className="border-b border-slate-100">
                      <td className="py-2.5 font-medium text-slate-700">{row.name}</td>
                      {[row.self, row.sup, row.peer, row.team, row.total].map((val, i) => (
                        <td key={i} className="text-center py-2.5">
                          <span
                            className={`inline-block w-10 py-0.5 rounded text-xs font-semibold ${
                              val >= 7.5
                                ? "bg-emerald-50 text-emerald-700"
                                : val >= 6.0
                                ? "bg-amber-50 text-amber-700"
                                : "bg-red-50 text-red-700"
                            }`}
                          >
                            {val.toFixed(1)}
                          </span>
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* New Round Tab */}
      {activeTab === "new" && (
        <div className="max-w-2xl">
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-6">
            <h3 className="text-lg font-semibold text-gr8-navy">Neue 360°-Feedback-Runde erstellen</h3>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Titel</label>
              <input
                type="text"
                placeholder="z.B. Q1 2025 — Führungsfeedback"
                className="w-full px-4 py-2.5 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-gr8-purple"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-3">Rater einladen</label>
              {PERSPECTIVES.filter((p) => p.key !== "self").map((p) => (
                <div key={p.key} className="mb-4">
                  <div className="flex items-center gap-2 mb-2">
                    <span>{p.icon}</span>
                    <span className="text-sm font-medium text-slate-700">{p.label}</span>
                    <span className="text-xs text-slate-400">(min. {p.min})</span>
                  </div>
                  <input
                    type="text"
                    placeholder="E-Mail-Adressen (kommagetrennt)"
                    className="w-full px-4 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:border-gr8-purple"
                  />
                </div>
              ))}
            </div>

            <div className="bg-slate-50 rounded-xl p-4">
              <h4 className="text-sm font-medium text-slate-700 mb-2">DSGVO-Hinweis</h4>
              <p className="text-xs text-slate-500">
                Alle Feedback-Geber müssen der DSGVO-konformen Verarbeitung zustimmen.
                Individuelle Antworten werden vollständig anonymisiert.
                Gruppen mit weniger als 3 Ratern werden nicht ausgewertet.
                Daten werden nach 24 Monaten automatisch gelöscht.
              </p>
            </div>

            <button className="w-full py-3 bg-gr8-navy hover:bg-gr8-navy-light text-white rounded-xl text-sm font-medium transition-colors">
              Feedback-Runde erstellen & Einladungen senden
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
