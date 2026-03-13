"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { useSessions } from "@/hooks/useSessions";
import { useSSEChat } from "@/hooks/useSSEChat";
import { ApiError } from "@/lib/api";
import { ThreePanelLayout } from "@/components/layout/ThreePanelLayout";
import { LeftSidebar } from "@/components/layout/LeftSidebar";
import { RightSidebar } from "@/components/layout/RightSidebar";
import { ChatPanel } from "@/components/chat/ChatPanel";

export default function DashboardPage() {
  const router = useRouter();
  const { user, isAuthenticated, isLoading: authLoading, logout } = useAuth();
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

  // Auth guard
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.replace("/login");
    }
  }, [authLoading, isAuthenticated, router]);

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
      // Load persisted suggestions
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
      // Check for 402 Payment Required (no valid code)
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

  const handleLogout = () => {
    logout();
    router.replace("/login");
  };

  if (authLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-surface-dark">
        <div className="flex gap-1">
          <div className="w-2 h-2 rounded-full bg-scil typing-dot" />
          <div className="w-2 h-2 rounded-full bg-scil typing-dot" />
          <div className="w-2 h-2 rounded-full bg-scil typing-dot" />
        </div>
      </div>
    );
  }

  if (!isAuthenticated) return null;

  return (
    <>
      {/* Code Required Banner */}
      {needsCode && (
        <div className="fixed top-0 left-0 right-0 z-50 bg-scil/95 backdrop-blur-sm px-4 py-3">
          <div className="max-w-3xl mx-auto flex items-center justify-between">
            <p className="text-white text-sm font-medium">
              Du benoetigst einen Diagnostik-Code, um eine neue Diagnostik zu starten.
            </p>
            <div className="flex gap-2 ml-4">
              <a
                href="/codes"
                className="px-3 py-1.5 bg-white text-scil-dark text-sm font-medium rounded-lg hover:bg-slate-100 transition-colors"
              >
                Codes kaufen
              </a>
              <a
                href="/redeem"
                className="px-3 py-1.5 bg-white/20 text-white text-sm font-medium rounded-lg hover:bg-white/30 transition-colors"
              >
                Code einloesen
              </a>
              <button
                onClick={() => setNeedsCode(false)}
                className="px-2 py-1.5 text-white/70 hover:text-white transition-colors"
              >
                ✕
              </button>
            </div>
          </div>
        </div>
      )}
      <ThreePanelLayout
        left={
          <LeftSidebar
            sessions={sessions}
            activeSessionId={activeSessionId}
            onCreateSession={handleCreateSession}
            onSelectSession={handleSelectSession}
            onDeleteSession={deleteSession}
            onLogout={handleLogout}
            isLoading={sessionsLoading}
            userRole={user?.role}
          />
        }
        center={
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
        }
        right={
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
      />
    </>
  );
}
