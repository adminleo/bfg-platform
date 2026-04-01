import { SCILPolygon } from "@/components/diagnostics/SCILPolygon";

const DEMO_SCORES = {
  sensus: { inner_presence: 7.2, conviction: 6.8, moment_focus: 7.5, emotionality: 5.9 },
  corpus: { appearance: 6.5, gesture: 5.8, facial_expression: 7.1, spatial_presence: 6.3 },
  intellektus: { analytics: 8.1, goal_orientation: 7.8, structure: 8.4, objectivity: 7.6 },
  lingua: { voice: 6.9, articulation: 7.3, eloquence: 7.0, imagery: 6.2 },
};

export default function Home() {
  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Hero */}
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-gr8-navy via-gr8-purple to-gr8-neon bg-clip-text text-transparent">
          Gr8hub Personal Development
        </h1>
        <p className="text-xl text-slate-500 max-w-2xl mx-auto">
          KI-gestützte Diagnostik. 360° Feedback. Personalisiertes Coaching. Echte Berater.
        </p>
      </div>

      {/* Dashboard Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* SCIL Polygon */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm">
          <h2 className="text-lg font-semibold text-gr8-navy mb-4">Dein SCIL-Profil</h2>
          <SCILPolygon scores={DEMO_SCORES} size={400} />
        </div>

        {/* Quick Actions */}
        <div className="space-y-4">
          <a href="/diagnostics" className="block bg-white rounded-2xl p-6 border border-slate-200 shadow-sm hover:border-gr8-purple transition-colors">
            <h3 className="text-lg font-semibold text-gr8-navy mb-2">Diagnostik starten</h3>
            <p className="text-slate-500 text-sm">
              Wähle aus 12+ Diagnostiken: SCIL, Big Five, Werte, EQ, Resilienz und mehr.
            </p>
            <div className="flex gap-2 mt-3">
              {["SCIL", "Big Five", "Werte", "EQ", "Resilienz"].map((d) => (
                <span key={d} className="px-2 py-1 bg-gr8-navy/5 text-gr8-navy rounded text-xs font-medium">{d}</span>
              ))}
            </div>
          </a>

          <a href="/feedback" className="block bg-white rounded-2xl p-6 border border-slate-200 shadow-sm hover:border-gr8-neon transition-colors">
            <h3 className="text-lg font-semibold text-gr8-navy mb-2">360° Feedback</h3>
            <p className="text-slate-500 text-sm">
              Starte eine Feedback-Runde mit Vorgesetzten, Peers und Teammitgliedern — KI-geführt und anonym.
            </p>
            <div className="flex gap-2 mt-3">
              {["Selbstbild", "Fremdbild", "Johari Window"].map((d) => (
                <span key={d} className="px-2 py-1 bg-gr8-neon/10 text-gr8-neon-dark rounded text-xs font-medium">{d}</span>
              ))}
            </div>
          </a>

          <a href="/coaching" className="block bg-white rounded-2xl p-6 border border-slate-200 shadow-sm hover:border-gr8-purple transition-colors">
            <h3 className="text-lg font-semibold text-gr8-navy mb-2">KI-Coaching</h3>
            <p className="text-slate-500 text-sm">
              Dein persönlicher Development Agent — situatives Coaching, tägliche Impulse, Entwicklungsplanung.
            </p>
          </a>

          <a href="/experts" className="block bg-white rounded-2xl p-6 border border-slate-200 shadow-sm hover:border-gr8-purple-light transition-colors">
            <h3 className="text-lg font-semibold text-gr8-navy mb-2">Berater finden</h3>
            <p className="text-slate-500 text-sm">
              Finde den perfekten Coach aus unserem Netzwerk — KI-basiertes Matching auf Basis deines Profils.
            </p>
          </a>

          <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm">
            <h3 className="text-lg font-semibold text-gr8-navy mb-2">Token-Status</h3>
            <div className="flex items-center gap-4 text-sm">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-gr8-neon" />
                <span className="text-slate-500">2 aktive Tokens</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-gr8-purple" />
                <span className="text-slate-500">1 zugewiesen</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
