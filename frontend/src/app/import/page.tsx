"use client";

import { useState } from "react";

const IMPORT_TOOLS = [
  {
    slug: "mbti",
    name: "MBTI®",
    description: "Myers-Briggs Type Indicator — 4-Buchstaben-Typ + Preference Scores",
    icon: "🧠",
    fields: ["Typ-Code (z.B. INTJ)", "E-I Score", "S-N Score", "T-F Score", "J-P Score"],
  },
  {
    slug: "disc",
    name: "DISC / DiSG®",
    description: "4 Verhaltensdimensionen: Dominance, Influence, Steadiness, Conscientiousness",
    icon: "📊",
    fields: ["D-Score (0-100)", "I-Score (0-100)", "S-Score (0-100)", "C-Score (0-100)"],
  },
  {
    slug: "insights",
    name: "Insights Discovery®",
    description: "4 Farbenergie-Scores: Fiery Red, Sunshine Yellow, Earth Green, Cool Blue",
    icon: "🎨",
    fields: ["Fiery Red", "Sunshine Yellow", "Earth Green", "Cool Blue"],
  },
  {
    slug: "hogan",
    name: "Hogan Assessments",
    description: "HPI, HDS (Derailer) und MVPI Scores",
    icon: "📋",
    fields: ["HPI Scores (JSON)", "HDS Scores (JSON)", "MVPI Scores (JSON)"],
  },
  {
    slug: "cliftonstrengths",
    name: "CliftonStrengths®",
    description: "Gallup — Top 5-34 Stärken-Ranking",
    icon: "💪",
    fields: ["Top-Stärken (kommagetrennt)"],
  },
  {
    slug: "reiss",
    name: "Reiss Motivation Profile®",
    description: "16 Grundmotive mit Scores von -2 bis +2",
    icon: "🎯",
    fields: ["16 Motiv-Scores"],
  },
  {
    slug: "lumina",
    name: "Lumina Spark®",
    description: "24 Qualitäten-Scores im Lumina-Modell",
    icon: "✨",
    fields: ["24 Qualitäten-Scores"],
  },
  {
    slug: "9levels",
    name: "9 Levels®",
    description: "Wertesystem-Level-Scores basierend auf Spiral Dynamics",
    icon: "🌀",
    fields: ["9 Level-Scores (0-100)"],
  },
  {
    slug: "pcm",
    name: "PCM®",
    description: "Process Communication Model — 6 Persönlichkeitstyp-Scores",
    icon: "🗣️",
    fields: ["Thinker", "Persister", "Harmonizer", "Imaginer", "Rebel", "Promoter"],
  },
  {
    slug: "hbdi",
    name: "HBDI®",
    description: "Herrmann Brain Dominance — 4-Quadranten Denkpräferenzen",
    icon: "🧩",
    fields: ["A-Analytical", "B-Practical", "C-Relational", "D-Experimental"],
  },
  {
    slug: "captain",
    name: "CAPTain®",
    description: "Potenzialanalyse — Kompetenz- und Potenzial-Scores",
    icon: "⚓",
    fields: ["Potenzial-Scores (JSON)"],
  },
  {
    slug: "biostruktur",
    name: "Biostruktur-Analyse®",
    description: "Structogram — 3-Farben-Profil (Grün/Rot/Blau)",
    icon: "🔬",
    fields: ["Grün (0-100)", "Rot (0-100)", "Blau (0-100)"],
  },
  {
    slug: "profilingvalues",
    name: "Profilingvalues®",
    description: "Werteprofil-Scores mit verschiedenen Dimensionen",
    icon: "💎",
    fields: ["Werte-Scores (JSON)"],
  },
];

export default function ImportPage() {
  const [selectedTool, setSelectedTool] = useState<string | null>(null);
  const [consent, setConsent] = useState(false);

  const tool = IMPORT_TOOLS.find((t) => t.slug === selectedTool);

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gr8-navy mb-2">Ergebnisse importieren</h1>
      <p className="text-slate-500 mb-8">
        Importiere Ergebnisse deiner bestehenden Diagnostik-Tests. Wir speichern ausschließlich Scores — keine Items oder Report-Texte.
      </p>

      {/* Info Banner */}
      <div className="bg-gradient-to-r from-gr8-purple to-gr8-navy rounded-2xl p-6 text-white mb-8">
        <h2 className="font-semibold mb-2">Wie funktioniert der Import?</h2>
        <p className="text-sm text-white/80 mb-3">
          Du gibst nur die numerischen Ergebnis-Scores deiner bestehenden Tests ein.
          Gr8hub kombiniert diese mit deinen eigenen Diagnostik-Ergebnissen für ein ganzheitliches Entwicklungsprofil.
        </p>
        <div className="flex gap-3">
          {["Nur Score-Werte", "DSGVO-konform", "13 Tools unterstützt", "Keine Items/Texte"].map((tag) => (
            <span key={tag} className="px-2.5 py-1 bg-white/10 rounded-lg text-xs">{tag}</span>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Tool Selection */}
        <div className="lg:col-span-1">
          <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-3">Diagnostik-Tool wählen</h3>
          <div className="space-y-2 max-h-[600px] overflow-y-auto pr-2">
            {IMPORT_TOOLS.map((t) => (
              <button
                key={t.slug}
                onClick={() => setSelectedTool(t.slug)}
                className={`w-full text-left p-3 rounded-xl border transition-colors ${
                  selectedTool === t.slug
                    ? "border-gr8-purple bg-gr8-purple/5"
                    : "border-slate-200 bg-white hover:border-slate-300"
                }`}
              >
                <div className="flex items-center gap-2">
                  <span className="text-lg">{t.icon}</span>
                  <span className="font-medium text-sm text-gr8-navy">{t.name}</span>
                </div>
                <p className="text-xs text-slate-500 mt-1 ml-7">{t.description}</p>
              </button>
            ))}
          </div>
        </div>

        {/* Import Form */}
        <div className="lg:col-span-2">
          {tool ? (
            <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
              <div className="flex items-center gap-3 mb-6">
                <span className="text-3xl">{tool.icon}</span>
                <div>
                  <h3 className="text-xl font-semibold text-gr8-navy">{tool.name}</h3>
                  <p className="text-sm text-slate-500">{tool.description}</p>
                </div>
              </div>

              <div className="space-y-4">
                {tool.fields.map((field) => (
                  <div key={field}>
                    <label className="block text-sm font-medium text-slate-700 mb-1">{field}</label>
                    <input
                      type="text"
                      placeholder={`${field} eingeben...`}
                      className="w-full px-4 py-2.5 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-gr8-purple"
                    />
                  </div>
                ))}

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Testdatum (optional)</label>
                  <input
                    type="date"
                    className="w-full px-4 py-2.5 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-gr8-purple"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Anbieter (optional)</label>
                  <input
                    type="text"
                    placeholder="z.B. Name des Coaches oder Instituts"
                    className="w-full px-4 py-2.5 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-gr8-purple"
                  />
                </div>

                {/* DSGVO Consent */}
                <div className="bg-slate-50 rounded-xl p-4">
                  <label className="flex items-start gap-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={consent}
                      onChange={(e) => setConsent(e.target.checked)}
                      className="mt-1 accent-gr8-purple"
                    />
                    <span className="text-xs text-slate-600">
                      Ich bestätige, dass ich berechtigt bin, diese Ergebnisse hochzuladen,
                      und willige in die Verarbeitung auf der Gr8hub-Plattform ein
                      (Art. 6 Abs. 1 lit. a DSGVO). Es werden ausschließlich Score-Werte
                      gespeichert — keine Items, Report-Texte oder urheberrechtlich geschützte Inhalte.
                    </span>
                  </label>
                </div>

                <button
                  disabled={!consent}
                  className="w-full py-3 bg-gr8-navy hover:bg-gr8-navy-light disabled:opacity-40 text-white rounded-xl text-sm font-medium transition-colors"
                >
                  Ergebnis importieren
                </button>
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-12 text-center">
              <p className="text-4xl mb-4">📥</p>
              <h3 className="text-lg font-semibold text-gr8-navy mb-2">Diagnostik-Tool wählen</h3>
              <p className="text-sm text-slate-500">
                Wähle links ein Diagnostik-Tool aus, um deine bestehenden Ergebnisse zu importieren.
              </p>
            </div>
          )}

          {/* IP Rights Notice */}
          <div className="mt-6 bg-amber-50 rounded-xl border border-amber-200 p-4">
            <h4 className="text-sm font-medium text-amber-800 mb-1">Hinweis zu Urheberrechten</h4>
            <p className="text-xs text-amber-700">
              Die genannten Diagnostik-Tools sind eingetragene Marken ihrer jeweiligen Rechteinhaber.
              Gr8hub importiert ausschließlich numerische Score-Werte mit Ihrer Einwilligung.
              Wir übernehmen keine Items, Fragebogen-Texte, Report-Bausteine oder geschützten Visualisierungen.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
