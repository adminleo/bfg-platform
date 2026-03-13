"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { RoleGuard } from "@/components/auth/RoleGuard";
import { useAuth } from "@/hooks/useAuth";

const NAV_ITEMS = [
  { href: "/coach", label: "Dashboard", icon: "📊" },
  { href: "/coach/coachees", label: "Coachees", icon: "👥" },
  { href: "/coach/codes", label: "Codes", icon: "🔑" },
  { href: "/coach/activity", label: "Aktivitaet", icon: "📋" },
];

export default function CoachLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
    router.replace("/login");
  };

  return (
    <RoleGuard allowedRoles={["coach", "admin"]}>
      <div className="flex min-h-screen bg-surface-dark">
        {/* Sidebar */}
        <aside className="w-64 border-r border-border bg-surface-dark flex flex-col">
          {/* Header */}
          <div className="p-4 border-b border-border">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-8 h-8 rounded-lg bg-scil flex items-center justify-center text-white font-bold text-sm">
                C
              </div>
              <span className="font-semibold text-white">Coach Dashboard</span>
            </div>
            <p className="text-xs text-slate-500 truncate">{user?.full_name}</p>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-3 space-y-1">
            {NAV_ITEMS.map((item) => {
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
                    isActive
                      ? "bg-scil/10 text-scil font-medium"
                      : "text-slate-400 hover:bg-surface hover:text-slate-200"
                  }`}
                >
                  <span>{item.icon}</span>
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>

          {/* Footer */}
          <div className="p-3 border-t border-border space-y-1">
            <Link
              href="/dashboard"
              className="flex items-center gap-3 px-3 py-2 text-sm text-slate-400 hover:text-slate-200 hover:bg-surface rounded-lg transition-colors"
            >
              <span>🔬</span>
              <span>Zur Diagnostik</span>
            </Link>
            <Link
              href="/codes"
              className="flex items-center gap-3 px-3 py-2 text-sm text-slate-400 hover:text-slate-200 hover:bg-surface rounded-lg transition-colors"
            >
              <span>🛒</span>
              <span>Codes kaufen</span>
            </Link>
            <button
              onClick={handleLogout}
              className="w-full flex items-center gap-3 px-3 py-2 text-sm text-slate-400 hover:text-slate-200 hover:bg-surface rounded-lg transition-colors text-left"
            >
              <span>🚪</span>
              <span>Abmelden</span>
            </button>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 overflow-auto">
          {children}
        </main>
      </div>
    </RoleGuard>
  );
}
