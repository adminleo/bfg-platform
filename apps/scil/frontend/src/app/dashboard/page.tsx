"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/hooks/useAuth";
import { useSessions } from "@/hooks/useSessions";
import { useSSEChat } from "@/hooks/useSSEChat";
import { ApiError } from "@/lib/api";
import { AppShell } from "@/components/layout/AppShell";
import { LeftSidebar } from "@/components/layout/LeftSidebar";
import { RightSidebar } from "@/components/layout/RightSidebar";
import { ChatPanel } from "@/components/chat/ChatPanel";

export default function DashboardPage() {
  const { user } = useAuth();
  const {
    sessions,
    activeSessionId,
    activeSession,
    isLoading: sessionsLoading,
    createSession,
    loadSession,
    deleteSession,
  } = useSessions();
  const {
    messages,
    scores,
    polygon,
    progress,
    clusterProgress,
    totalScored,
    isStreaming,
    isComplete,
    resultId,
    suggestions,
    setSuggestions,
    sendMessage,
    loadConversation,
    setScores,
    setPolygon,
    setClusterProgress,
  } = useSSEChat();

  // Load conversation when switching sessions
  useEffect(() => {
    if (activeSession) {
      loadConversation(activeSession.conversation);
      if (activeSession.scores) {
        setScores(activeSession.scores);
      }
      if (activeSession.polygon) {
        setPolygon(activeSession.polygon);
      }
      if (activeSession.cluster_progress) {
        setClusterProgress(activeSession.cluster_progress);
      }
      if (activeSession.suggestions && activeSession.suggestions.length > 0) {
        setSuggestions(activeSession.suggestions);
      } else {
        setSuggestions([]);
      }
    }
  }, [activeSession, loadConversation, setScores, setPolygon, setClusterProgress, setSuggestions]);

  const [needsCode, setNeedsCode] = useState(false);

  const handleCreateSession = async () => {
    setNeedsCode(false);
    try {
      const session = await createSession();
      if (session) {
        await loadSession(session.id);
      }
    } catch (e: unknown) {
      if (e instanceof ApiError && e.status === 402) {
        setNeedsCode(true);
      }
    }
  };

  const handleSelectSession = async (id: string) => {
    await loadSession(id);
  };

  const handleSendMessage = async (text: string) => {
    if (!activeSessionId) return;
    await sendMessage(activeSessionId, text);
  };

  const scilHeader = (
    <div className="p-4">
      <div className="flex items-center gap-2">
        <div className="w-8 h-8 rounded-xl bg-scil flex items-center justify-center text-slate-900 font-bold text-sm shadow-lg shadow-scil/20">
          S
        </div>
        <span className="font-semibold text-slate-900">S.C.I.L. Profile</span>
      </div>
    </div>
  );

  return (
    <>
      {/* Code Required Banner */}
      {needsCode && (
        <div className="fixed top-0 left-0 right-0 z-50 glass-strong bg-gradient-to-r from-scil/80 to-scil-dark/80 px-4 py-3 animate-fade-in-up">
          <div className="max-w-3xl mx-auto flex items-center justify-between">
            <p className="text-slate-900 text-sm font-medium">
              Du benoetigst einen Diagnostik-Code, um eine neue Diagnostik zu starten.
            </p>
            <div className="flex gap-2 ml-4">
              <a
                href="/codes"
                className="btn-glass text-white font-medium rounded-xl px-3 py-1.5 text-sm"
              >
                Codes kaufen
              </a>
              <a
                href="/redeem"
                className="btn-ghost text-slate-600 rounded-xl px-3 py-1.5 text-sm"
              >
                Code einloesen
              </a>
              <button
                onClick={() => setNeedsCode(false)}
                className="px-2 py-1.5 text-white/70 hover:text-white transition-colors"
              >
                &#x2715;
              </button>
            </div>
          </div>
        </div>
      )}
      <AppShell
        leftHeader={scilHeader}
        leftSidebar={
          <LeftSidebar
            sessions={sessions}
            activeSessionId={activeSessionId}
            onCreateSession={handleCreateSession}
            onSelectSession={handleSelectSession}
            onDeleteSession={deleteSession}
            isLoading={sessionsLoading}
          />
        }
        rightSidebar={
          <RightSidebar
            scores={scores}
            polygon={polygon}
            progress={progress}
            isComplete={isComplete}
            resultId={resultId}
            sessionId={activeSessionId}
            clusterProgress={clusterProgress}
            totalScored={totalScored}
          />
        }
      >
        <div className="h-full animate-fade-in-up">
          <ChatPanel
            messages={messages}
            isStreaming={isStreaming}
            isComplete={isComplete}
            progress={progress}
            onSendMessage={handleSendMessage}
            onStartSession={handleCreateSession}
            hasSession={!!activeSessionId}
            suggestions={suggestions}
            onSelectSuggestion={handleSendMessage}
          />
        </div>
      </AppShell>
    </>
  );
}
