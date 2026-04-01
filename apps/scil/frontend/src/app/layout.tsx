import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "S.C.I.L. Profile — Wirkungsdiagnostik",
  description: "Entdecke dein Wirkungsprofil mit der S.C.I.L. Performance Strategie",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="de">
      <body className="font-sans">{children}</body>
    </html>
  );
}
