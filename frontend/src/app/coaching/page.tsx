"use client";

import { ChatInterface } from "@/components/chat/ChatInterface";

export default function CoachingPage() {
  const agentUrl = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8001";

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gr8-navy mb-2">KI-Coaching</h1>
      <p className="text-slate-500 mb-6">Dein persönlicher Development Agent — immer bereit für Coaching, Impulse und Entwicklungsplanung.</p>

      <div className="h-[600px]">
        <ChatInterface
          wsUrl={`${agentUrl}/ws/coaching/demo-user`}
          title="Gr8hub Coaching Agent"
        />
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
        {[
          "Mein Profil besprechen",
          "Präsentation vorbereiten",
          "Entwicklungsplan erstellen",
          "Täglicher Check-in",
        ].map((action) => (
          <button
            key={action}
            className="p-3 bg-white border border-slate-200 shadow-sm rounded-xl text-sm text-slate-600 hover:border-gr8-purple hover:text-gr8-navy transition-colors"
          >
            {action}
          </button>
        ))}
      </div>
    </div>
  );
}
