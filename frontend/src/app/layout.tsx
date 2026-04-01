import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Gr8hub — Personal Development Platform",
  description: "KI-gestützte Persönlichkeitsdiagnostik, 360° Feedback und Coaching",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="de">
      <body className="min-h-screen">
        <nav className="border-b border-slate-200 bg-white/80 backdrop-blur-sm sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
            <a href="/" className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-gr8-navy via-gr8-purple to-gr8-neon" />
              <span className="text-lg font-bold text-gr8-navy">Gr8hub</span>
            </a>
            <div className="flex items-center gap-6 text-sm text-slate-500">
              <a href="/" className="hover:text-gr8-navy transition-colors">Dashboard</a>
              <a href="/diagnostics" className="hover:text-gr8-navy transition-colors">Diagnostik</a>
              <a href="/feedback" className="hover:text-gr8-navy transition-colors">360° Feedback</a>
              <a href="/coaching" className="hover:text-gr8-navy transition-colors">Coaching</a>
              <a href="/import" className="hover:text-gr8-navy transition-colors">Import</a>
              <a href="/experts" className="hover:text-gr8-navy transition-colors">Berater</a>
            </div>
          </div>
        </nav>
        <main>{children}</main>
      </body>
    </html>
  );
}
