const DEMO_EXPERTS = [
  {
    id: "1",
    name: "Dr. Maria Schneider",
    title: "SCIL Master & Executive Coach",
    specializations: ["Führungskommunikation", "Charisma-Entwicklung", "Präsentationstraining"],
    certifications: ["SCIL Master", "ICF PCC", "Hogan Certified"],
    languages: ["Deutsch", "Englisch"],
    rating: 4.9,
    sessions: 342,
    hourlyRate: 250,
  },
  {
    id: "2",
    name: "Thomas Weber",
    title: "Resilienz-Coach & Trainer",
    specializations: ["Resilienz", "Burnout-Prävention", "Stressmanagement"],
    certifications: ["SCIL Professional", "DBVC Coach", "CD-RISC Certified"],
    languages: ["Deutsch"],
    rating: 4.8,
    sessions: 218,
    hourlyRate: 180,
  },
  {
    id: "3",
    name: "Sarah van der Berg",
    title: "Team-Entwicklung & OE-Beratung",
    specializations: ["Teamdynamik", "Organisationsentwicklung", "360°-Feedback"],
    certifications: ["SCIL Master", "ICF MCC", "Belbin Accredited"],
    languages: ["Deutsch", "Englisch", "Niederländisch"],
    rating: 4.9,
    sessions: 456,
    hourlyRate: 280,
  },
];

export default function ExpertsPage() {
  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gr8-navy mb-2">Berater-Netzwerk</h1>
      <p className="text-slate-500 mb-8">KI-basiertes Matching mit zertifizierten Experten auf Basis deines Diagnostik-Profils.</p>

      {/* Match Quality Banner */}
      <div className="bg-gradient-to-r from-gr8-navy to-gr8-purple rounded-2xl p-6 text-white mb-8">
        <h2 className="font-semibold mb-2">Personalisiertes Matching</h2>
        <p className="text-sm text-white/80">
          Basierend auf deinem Gr8hub-Profil und deinen Entwicklungszielen empfehlen wir dir die passendsten Berater.
          Unser Algorithmus berücksichtigt Diagnostik-Fit, Methodik-Fit, Erfahrung und historische Erfolgsquote.
        </p>
      </div>

      {/* Expert Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {DEMO_EXPERTS.map((expert) => (
          <div key={expert.id} className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden hover:border-gr8-purple transition-colors">
            <div className="p-6">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="font-semibold text-gr8-navy">{expert.name}</h3>
                  <p className="text-sm text-slate-500">{expert.title}</p>
                </div>
                <div className="flex items-center gap-1 bg-amber-50 px-2 py-1 rounded-lg">
                  <span className="text-amber-500 text-xs">★</span>
                  <span className="text-xs font-medium text-amber-700">{expert.rating}</span>
                </div>
              </div>

              {/* Specializations */}
              <div className="flex flex-wrap gap-1.5 mb-3">
                {expert.specializations.map((s) => (
                  <span key={s} className="px-2 py-0.5 bg-slate-100 rounded text-xs text-slate-600">{s}</span>
                ))}
              </div>

              {/* Certifications */}
              <div className="flex flex-wrap gap-1.5 mb-4">
                {expert.certifications.map((c) => (
                  <span key={c} className="px-2 py-0.5 bg-gr8-purple/5 border border-gr8-purple/20 rounded text-xs text-gr8-purple">{c}</span>
                ))}
              </div>

              {/* Stats */}
              <div className="flex items-center justify-between text-sm text-slate-500 mb-4">
                <span>{expert.sessions} Sessions</span>
                <span>{expert.languages.join(", ")}</span>
                <span className="font-semibold text-gr8-navy">{expert.hourlyRate}€/h</span>
              </div>

              <button className="w-full py-2.5 bg-gr8-navy hover:bg-gr8-navy-light text-white rounded-xl text-sm font-medium transition-colors">
                Termin buchen
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
