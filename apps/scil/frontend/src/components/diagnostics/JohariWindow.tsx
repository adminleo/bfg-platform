"use client";

interface JohariData {
  public: string[];
  blind_spot: string[];
  hidden: string[];
  unknown: string[];
}

interface JohariWindowProps {
  data: JohariData;
  competencyLabels?: Record<string, string>;
}

const DEFAULT_LABELS: Record<string, string> = {
  persuasion: "Überzeugungskraft",
  analytical_thinking: "Analytisches Denken",
  empathy: "Empathie",
  presence: "Präsenz & Auftreten",
  strategic_thinking: "Strategisches Denken",
  storytelling: "Storytelling",
  team_leadership: "Teamführung",
  clarity: "Klarheit",
};

const QUADRANTS = [
  {
    key: "public" as const,
    title: "Öffentlich",
    subtitle: "Selbst & Andere sehen es",
    color: "bg-emerald-50 border-emerald-200",
    badgeColor: "bg-emerald-100 text-emerald-700",
    icon: "👁️",
    description: "Bestätigte Stärken — weiter ausbauen",
  },
  {
    key: "blind_spot" as const,
    title: "Blinder Fleck",
    subtitle: "Andere sehen es, du nicht",
    color: "bg-amber-50 border-amber-200",
    badgeColor: "bg-amber-100 text-amber-700",
    icon: "🔍",
    description: "Entwicklungsfelder — Coach kann helfen",
  },
  {
    key: "hidden" as const,
    title: "Verborgen",
    subtitle: "Du siehst es, Andere nicht",
    color: "bg-indigo-50 border-indigo-200",
    badgeColor: "bg-indigo-100 text-indigo-700",
    icon: "🙈",
    description: "Ungenutztes Potenzial — Sichtbarkeit erhöhen",
  },
  {
    key: "unknown" as const,
    title: "Unbekannt",
    subtitle: "Weder du noch Andere",
    color: "bg-slate-50 border-slate-200",
    badgeColor: "bg-slate-100 text-slate-600",
    icon: "❓",
    description: "Terra incognita — experimentieren",
  },
];

export function JohariWindow({ data, competencyLabels = DEFAULT_LABELS }: JohariWindowProps) {
  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="text-center">
        <h3 className="text-lg font-semibold text-slate-900">Johari-Fenster</h3>
        <p className="text-sm text-slate-500">Selbstbild vs. Fremdbild — Wo stimmt die Wahrnehmung überein?</p>
      </div>

      {/* Axis labels */}
      <div className="relative">
        {/* Top label */}
        <div className="flex justify-center mb-2">
          <div className="flex gap-4 text-xs text-slate-500 font-medium">
            <span className="w-[calc(50%-0.5rem)] text-center">Mir bekannt</span>
            <span className="w-[calc(50%-0.5rem)] text-center">Mir unbekannt</span>
          </div>
        </div>

        <div className="flex">
          {/* Left label */}
          <div className="flex flex-col justify-center w-6 mr-2">
            <div className="flex flex-col items-center gap-1">
              <span className="text-xs text-slate-500 font-medium [writing-mode:vertical-lr] rotate-180">Anderen bekannt</span>
            </div>
          </div>

          {/* Grid */}
          <div className="grid grid-cols-2 gap-3 flex-1">
            {QUADRANTS.map((q) => (
              <div
                key={q.key}
                className={`rounded-xl border-2 p-4 ${q.color} min-h-[160px]`}
              >
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-lg">{q.icon}</span>
                  <div>
                    <h4 className="font-semibold text-sm text-slate-800">{q.title}</h4>
                    <p className="text-[11px] text-slate-500">{q.subtitle}</p>
                  </div>
                </div>

                {data[q.key].length > 0 ? (
                  <div className="flex flex-wrap gap-1.5 mt-2">
                    {data[q.key].map((comp) => (
                      <span
                        key={comp}
                        className={`px-2 py-0.5 rounded-full text-xs font-medium ${q.badgeColor}`}
                      >
                        {competencyLabels[comp] || comp}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-slate-400 italic mt-2">Keine Kompetenzen in diesem Quadranten</p>
                )}

                <p className="text-[10px] text-slate-400 mt-3">{q.description}</p>
              </div>
            ))}
          </div>

          {/* Right label */}
          <div className="flex flex-col justify-center w-6 ml-2">
            <div className="flex flex-col items-center gap-1">
              <span className="text-xs text-slate-500 font-medium [writing-mode:vertical-lr] rotate-180">Anderen unbekannt</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
