"use client";

import { Suspense, useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useCodes } from "@/hooks/useCodes";
import { api } from "@/lib/api";
import { AppShell } from "@/components/layout/AppShell";
import { ResourcesSidebar } from "@/components/resources/ResourcesSidebar";
import type { CodePackage, TrainingContentItem } from "@/lib/types";

const TABS = [
  { key: "codes", label: "Diagnostik-Codes" },
  { key: "trainings", label: "Trainings" },
  { key: "books", label: "Buecher & Materialien" },
] as const;

type TabKey = (typeof TABS)[number]["key"];

const AREA_CONFIG: Record<string, { label: string; color: string; bgColor: string }> = {
  sensus: { label: "Sensus", color: "text-rose-400", bgColor: "bg-rose-500/20" },
  corpus: { label: "Corpus", color: "text-amber-400", bgColor: "bg-amber-500/20" },
  intellektus: { label: "Intellektus", color: "text-blue-400", bgColor: "bg-blue-500/20" },
  lingua: { label: "Lingua", color: "text-emerald-400", bgColor: "bg-emerald-500/20" },
  general: { label: "Allgemein", color: "text-slate-400", bgColor: "bg-slate-500/20" },
};

function PackageCard({
  pkg,
  onBuy,
  onDevBuy,
  isLoading,
  isDev,
}: {
  pkg: CodePackage;
  onBuy: () => void;
  onDevBuy: () => void;
  isLoading: boolean;
  isDev: boolean;
}) {
  const unitPrice = (pkg.unit_price_cents / 100).toFixed(2);
  const totalPrice = (pkg.total_price_cents / 100).toFixed(2);

  return (
    <div className="glass-card p-6 flex flex-col">
      <div className="flex-1">
        <div className="flex items-start justify-between mb-3">
          <h3 className="text-lg font-semibold text-slate-900">{pkg.label}</h3>
          {pkg.savings_percent > 0 && (
            <span className="bg-scil/20 text-scil text-xs font-medium px-2 py-1 rounded-full">
              -{pkg.savings_percent}%
            </span>
          )}
        </div>
        <div className="mb-4">
          <span className="text-3xl font-bold text-slate-900 stat-number">
            {unitPrice} EUR
          </span>
          <span className="text-slate-500 text-sm ml-1">/ Code</span>
        </div>
        {pkg.quantity > 1 && (
          <p className="text-slate-500 text-sm mb-4">
            {pkg.quantity} Codes = {totalPrice} EUR gesamt
          </p>
        )}
      </div>
      <div className="flex flex-col gap-2">
        <button
          onClick={onBuy}
          disabled={isLoading}
          className="w-full py-2.5 btn-glass text-white font-medium
                     rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? "Wird verarbeitet..." : "Jetzt kaufen"}
        </button>
        {isDev && (
          <button
            onClick={onDevBuy}
            disabled={isLoading}
            className="w-full py-2 btn-ghost text-slate-600
                       text-sm rounded-xl transition-colors
                       disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Dev: Gratis generieren
          </button>
        )}
      </div>
    </div>
  );
}

function TrainingContentCard({ item }: { item: TrainingContentItem }) {
  const router = useRouter();
  const area = AREA_CONFIG[item.area] || AREA_CONFIG.general;

  return (
    <div className="glass-card p-6 flex flex-col">
      <div className="flex-1">
        {/* Area badge + premium indicator */}
        <div className="flex items-center justify-between mb-3">
          <span className={`inline-flex items-center gap-1 text-[10px] font-medium px-2.5 py-1 rounded-full ${area.bgColor} ${area.color}`}>
            {area.label}
          </span>
          {item.is_premium && item.price_cents != null && (
            <span className="text-sm font-bold text-slate-900 stat-number">
              {(item.price_cents / 100).toFixed(2)} EUR
            </span>
          )}
        </div>

        {/* Title */}
        <h3 className="text-lg font-semibold text-slate-900 mb-2 line-clamp-2">{item.title}</h3>

        {/* Description */}
        <p className="text-slate-500 text-sm mb-4 line-clamp-3">{item.description}</p>

        {/* Author + Duration */}
        <div className="flex flex-wrap items-center gap-3 text-xs text-slate-400 mb-4">
          {item.author && (
            <div className="flex items-center gap-1.5">
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              <span>{item.author}</span>
            </div>
          )}
          <div className="flex items-center gap-1.5">
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>{item.duration_minutes} Min.</span>
          </div>
          {item.lesson_count > 0 && (
            <div className="flex items-center gap-1.5">
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h7" />
              </svg>
              <span>{item.lesson_count} Lektionen</span>
            </div>
          )}
        </div>
      </div>

      {/* CTA button */}
      <button
        onClick={() => router.push(`/training/${item.id}`)}
        className="w-full py-2.5 btn-glass text-white font-medium
                   rounded-xl transition-colors flex items-center justify-center gap-2"
      >
        Mehr erfahren
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
      </button>
    </div>
  );
}

function BookPlaceholderCard({
  title,
  author,
  description,
}: {
  title: string;
  author: string;
  description: string;
}) {
  return (
    <div className="glass-card p-6 flex flex-col opacity-75">
      <div className="flex items-start gap-4 mb-4">
        <div className="w-16 h-20 rounded-lg bg-black/[0.02] border border-black/[0.06] flex items-center justify-center flex-shrink-0 text-slate-300">
          <svg
            className="w-8 h-8"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
            />
          </svg>
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-semibold text-slate-900 mb-1">{title}</h3>
          <p className="text-sm text-slate-400 mb-2">{author}</p>
          <p className="text-slate-500 text-sm">{description}</p>
        </div>
      </div>
      <div className="mt-auto">
        <span className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-black/[0.02] border border-black/[0.06] rounded-full text-xs font-medium text-slate-500">
          <svg
            className="w-3.5 h-3.5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          Demnachst verfuegbar
        </span>
      </div>
    </div>
  );
}

function ResourcesPageContent() {
  const searchParams = useSearchParams();
  const { codes, packages, isLoading, error, purchasePackage, devPurchase } =
    useCodes();
  const initialTab = (searchParams.get("tab") as TabKey) || "codes";
  const [activeTab, setActiveTab] = useState<TabKey>(
    TABS.some((t) => t.key === initialTab) ? initialTab : "codes"
  );
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [trainings, setTrainings] = useState<TrainingContentItem[]>([]);
  const [trainingsLoading, setTrainingsLoading] = useState(false);
  const [trainingsError, setTrainingsError] = useState<string | null>(null);

  const isDev =
    process.env.NODE_ENV === "development" ||
    (typeof window !== "undefined" &&
      (window.location.hostname === "localhost" || window.location.hostname.includes("vercel.app")));

  const purchaseCount = codes.length;

  // Fetch training content when trainings tab is selected
  useEffect(() => {
    if (activeTab === "trainings" && trainings.length === 0 && !trainingsLoading) {
      setTrainingsLoading(true);
      setTrainingsError(null);
      api
        .get<TrainingContentItem[]>("/training/content")
        .then((data) => {
          // Show premium trainings first, then all others
          const sorted = [...data].sort((a, b) => {
            if (a.is_premium && !b.is_premium) return -1;
            if (!a.is_premium && b.is_premium) return 1;
            return a.sort_order - b.sort_order;
          });
          setTrainings(sorted);
        })
        .catch((e) => {
          setTrainingsError(
            e instanceof Error ? e.message : "Fehler beim Laden der Trainings"
          );
        })
        .finally(() => setTrainingsLoading(false));
    }
  }, [activeTab, trainings.length, trainingsLoading]);

  const handleDevPurchase = async (packageType: string) => {
    const purchase = await devPurchase(packageType);
    if (purchase) {
      setSuccessMsg(
        "Code generiert und aktiviert! Du kannst jetzt eine Diagnostik starten."
      );
      setTimeout(() => setSuccessMsg(null), 5000);
    }
  };

  const handleTabChange = (tab: string) => {
    setActiveTab(tab as TabKey);
  };

  return (
    <AppShell
      leftSidebar={
        <ResourcesSidebar
          codes={codes}
          activeTab={activeTab}
          onTabChange={handleTabChange}
          purchaseCount={purchaseCount}
        />
      }
      rightDefaultOpen={false}
    >
      <div className="w-full px-6 py-6">
        {/* Success message */}
        {successMsg && (
          <div className="mb-6 p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-emerald-400 text-sm animate-fade-in-up flex items-center justify-between">
            <div className="flex items-center gap-2">
              <svg
                className="w-5 h-5 flex-shrink-0"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <span>{successMsg}</span>
            </div>
            <a
              href="/dashboard"
              className="ml-4 px-3 py-1.5 text-xs font-medium text-white bg-emerald-500/80 hover:bg-emerald-500 rounded-lg transition-all flex-shrink-0"
            >
              Zur Diagnostik
            </a>
          </div>
        )}

        {error && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-sm animate-fade-in-up">
            {error}
          </div>
        )}

        {/* Page header */}
        <div className="mb-6 animate-fade-in-up">
          <h1 className="text-xl font-bold text-slate-900">Ressourcen</h1>
          <p className="text-slate-500 text-sm mt-1">
            Codes, Trainings und Materialien fuer die SCIL-Diagnostik
          </p>
        </div>

        {/* Tabs */}
        <div className="flex flex-wrap items-center gap-2 mb-8 animate-fade-in-up">
          {TABS.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`px-4 py-2 text-sm font-medium rounded-full transition-all ${
                activeTab === tab.key
                  ? "bg-scil text-white"
                  : "bg-black/[0.02] text-slate-500 border border-black/[0.06] hover:bg-black/[0.04]"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab content */}
        {activeTab === "codes" && (
          <div className="animate-fade-in-up">
            <div className="mb-4">
              <h2 className="text-lg font-semibold text-slate-900">
                SCIL Diagnostik-Codes
              </h2>
              <p className="text-slate-500 text-sm mt-1">
                Kaufe Codes fuer die SCIL-Wirkungsdiagnostik
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {packages.map((pkg, index) => (
                <div
                  key={pkg.type}
                  className={`stagger-${Math.min(index + 1, 6)} animate-fade-in-up`}
                >
                  <PackageCard
                    pkg={pkg}
                    onBuy={() => purchasePackage(pkg.type)}
                    onDevBuy={() => handleDevPurchase(pkg.type)}
                    isLoading={isLoading}
                    isDev={isDev}
                  />
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === "trainings" && (
          <div className="animate-fade-in-up">
            <div className="mb-4">
              <h2 className="text-lg font-semibold text-slate-900">
                SCIL Trainings
              </h2>
              <p className="text-slate-500 text-sm mt-1">
                Vertiefte Trainingsprogramme fuer Ihre Kompetenzentwicklung
              </p>
            </div>

            {trainingsLoading && (
              <div className="flex items-center justify-center py-12">
                <div className="flex gap-1">
                  <div className="w-2 h-2 rounded-full bg-scil typing-dot" />
                  <div className="w-2 h-2 rounded-full bg-scil typing-dot" />
                  <div className="w-2 h-2 rounded-full bg-scil typing-dot" />
                </div>
              </div>
            )}

            {trainingsError && (
              <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-sm animate-fade-in-up">
                {trainingsError}
              </div>
            )}

            {!trainingsLoading && !trainingsError && trainings.length === 0 && (
              <div className="glass-card rounded-2xl p-8 text-center">
                <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-black/[0.04] flex items-center justify-center">
                  <svg className="w-6 h-6 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                  </svg>
                </div>
                <p className="text-sm text-slate-500">
                  Noch keine Trainings verfuegbar.
                </p>
              </div>
            )}

            {!trainingsLoading && trainings.length > 0 && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {trainings.map((item, index) => (
                  <div
                    key={item.id}
                    className={`stagger-${Math.min(index + 1, 6)} animate-fade-in-up`}
                  >
                    <TrainingContentCard item={item} />
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === "books" && (
          <div className="animate-fade-in-up">
            <div className="mb-4">
              <h2 className="text-lg font-semibold text-slate-900">
                Buecher &amp; Materialien
              </h2>
              <p className="text-slate-500 text-sm mt-1">
                Fachliteratur und Arbeitsmaterialien zur SCIL-Methodik
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <BookPlaceholderCard
                title="SCIL Praxishandbuch"
                author="SCIL Performance Academy"
                description="Das umfassende Handbuch zur SCIL-Wirkungsdiagnostik mit praktischen Uebungen und Fallbeispielen."
              />
              <BookPlaceholderCard
                title="Wirkungskompetenz entwickeln"
                author="SCIL Performance Academy"
                description="Strategien und Methoden zur gezielten Entwicklung Ihrer Wirkungskompetenzen in allen vier SCIL-Bereichen."
              />
              <BookPlaceholderCard
                title="SCIL Arbeitsblatt-Set"
                author="SCIL Performance Academy"
                description="Sammlung von Arbeitsblaettern und Reflexionsuebungen fuer den taeglichen Einsatz im Coaching und Training."
              />
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}

export default function ResourcesPage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center min-h-screen">
        <div className="flex gap-1">
          <div className="w-2 h-2 rounded-full bg-scil typing-dot" />
          <div className="w-2 h-2 rounded-full bg-scil typing-dot" />
          <div className="w-2 h-2 rounded-full bg-scil typing-dot" />
        </div>
      </div>
    }>
      <ResourcesPageContent />
    </Suspense>
  );
}
