const DIAGNOSTICS = [
  {
    slug: "scil",
    name: "S.C.I.L. Profile",
    description: "Misst deine kommunikative Wirkung über 4 Frequenzbereiche mit 16 Faktoren.",
    category: "Wirkungskompetenz",
    color: "from-scil-sensus to-scil-corpus",
    tiers: ["S", "M", "L", "XL"],
  },
  {
    slug: "big_five",
    name: "Big Five (OCEAN)",
    description: "Der wissenschaftliche Goldstandard: Offenheit, Gewissenhaftigkeit, Extraversion, Verträglichkeit, Neurotizismus.",
    category: "Persönlichkeit",
    color: "from-gr8-navy to-gr8-purple",
    tiers: ["S", "M", "L", "XL"],
  },
  {
    slug: "values_schwartz",
    name: "Werteprofil (Schwartz)",
    description: "Identifiziert deine 19 universellen Grundwerte und ihre Hierarchie.",
    category: "Werte",
    color: "from-gr8-purple to-gr8-purple-light",
    tiers: ["S", "M", "L", "XL"],
  },
  {
    slug: "eq_trait",
    name: "Emotionale Intelligenz",
    description: "15 Facetten: Wie gut erkennst und steuerst du Emotionen?",
    category: "EQ",
    color: "from-scil-sensus to-gr8-purple",
    tiers: ["S", "M", "L", "XL"],
  },
  {
    slug: "resilience",
    name: "Resilienz-Profil",
    description: "Deine psychische Widerstandsfähigkeit und Erholungskraft.",
    category: "Resilienz",
    color: "from-gr8-neon to-teal-400",
    tiers: ["S", "M", "L", "XL"],
  },
  {
    slug: "stress_coping",
    name: "Stressbewältigung",
    description: "Analysiert dein Stressverhalten und Coping-Strategien.",
    category: "Stress",
    color: "from-amber-400 to-orange-500",
    tiers: ["S", "M", "L", "XL"],
  },
  {
    slug: "team_roles",
    name: "Teamrollen",
    description: "Entdecke dein Beitragsprofil in Teams — Big-Five-basiert abgeleitet.",
    category: "Team",
    color: "from-scil-intellektus to-blue-400",
    tiers: ["S", "M", "L", "XL"],
  },
  {
    slug: "communication_style",
    name: "Kommunikationsstil",
    description: "NLP-basierte Analyse deiner Kommunikationspräferenzen.",
    category: "Kommunikation",
    color: "from-scil-lingua to-gr8-neon",
    tiers: ["S", "M", "L", "XL"],
  },
  {
    slug: "motivation_sdt",
    name: "Motivation (SDT)",
    description: "Intrinsische und extrinsische Motivation nach Self-Determination Theory.",
    category: "Motivation",
    color: "from-gr8-neon-dark to-emerald-400",
    tiers: ["S", "M", "L", "XL"],
  },
  {
    slug: "thinking_styles",
    name: "Denkstilpräferenzen",
    description: "4-Quadranten Denkmuster — eigenes Modell inspiriert von Whole Brain Thinking.",
    category: "Kognition",
    color: "from-gr8-purple-dark to-indigo-400",
    tiers: ["S", "M", "L", "XL"],
  },
  {
    slug: "cognitive_flexibility",
    name: "Kognitive Flexibilität",
    description: "IRT-basierte adaptive Denkaufgaben zur Messung deiner mentalen Agilität.",
    category: "Kognition",
    color: "from-cyan-400 to-gr8-navy",
    tiers: ["S", "M", "L", "XL"],
  },
  {
    slug: "feedback_360",
    name: "360° Feedback",
    description: "KI-geführtes Multi-Rater-Feedback mit Johari-Window und SCIL-Mapping.",
    category: "360° Feedback",
    color: "from-gr8-navy to-gr8-neon",
    tiers: ["M", "L", "XL"],
  },
];

const TIER_INFO: Record<string, { label: string; price: string; desc: string }> = {
  S: { label: "Small", price: "9-19€", desc: "Quick-Check" },
  M: { label: "Medium", price: "49-89€", desc: "Tiefenevaluation" },
  L: { label: "Large", price: "199-349€", desc: "+ Expert Coaching" },
  XL: { label: "Extra Large", price: "599-999€", desc: "Premium Package" },
};

export default function DiagnosticsPage() {
  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gr8-navy mb-2">Diagnostik-Suite</h1>
      <p className="text-slate-500 mb-8">Wähle deine Diagnostik und dein Tier. Jeder Run benötigt einen Token.</p>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {DIAGNOSTICS.map((d) => (
          <div key={d.slug} className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden hover:border-gr8-purple transition-colors">
            <div className={`h-1.5 bg-gradient-to-r ${d.color}`} />
            <div className="p-6">
              <span className="text-xs text-slate-400 uppercase tracking-wider">{d.category}</span>
              <h3 className="text-lg font-semibold text-gr8-navy mt-1 mb-2">{d.name}</h3>
              <p className="text-sm text-slate-500 mb-4">{d.description}</p>

              {/* Tier buttons */}
              <div className="grid grid-cols-4 gap-2">
                {d.tiers.map((tier) => (
                  <button
                    key={tier}
                    className="flex flex-col items-center p-2 rounded-lg bg-slate-50 hover:bg-gr8-navy/5 border border-slate-100 hover:border-gr8-purple transition-colors text-center"
                  >
                    <span className="text-xs font-bold text-gr8-navy">{tier}</span>
                    <span className="text-[10px] text-slate-400">{TIER_INFO[tier].price}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Bundle section */}
      <div className="mt-12">
        <h2 className="text-2xl font-bold text-gr8-navy mb-6">Bundles</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            { name: "Starter", desc: "1× SCIL (M) + 1× Big Five (M)", discount: "15%", price: "ab 83€" },
            { name: "Professional", desc: "3× Diagnostiken (M) + 1× Coaching", discount: "20%", price: "ab 176€" },
            { name: "Full Suite", desc: "Alle 12 Diagnostiken (M) + 2× Coaching", discount: "30%", price: "ab 315€" },
          ].map((b) => (
            <div key={b.name} className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-semibold text-gr8-navy">{b.name}</h3>
                <span className="px-2 py-0.5 bg-gr8-neon/10 text-gr8-neon-dark rounded text-xs font-medium">-{b.discount}</span>
              </div>
              <p className="text-sm text-slate-500 mb-3">{b.desc}</p>
              <p className="text-lg font-bold text-gr8-navy">{b.price}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
