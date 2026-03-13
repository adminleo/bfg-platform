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

  const isCoach = user?.role === "coach" || user?.role === "admin";

  const navItems = [
    {
      label: "Diagnostik",
      href: "/dashboard",
      icon: (
        <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
      ),
    },
    {
      label: "Training",
      href: "/training",
      icon: (
        <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      ),
    },
    {
      label: "Buchungen",
      href: "/bookings",
      icon: (
        <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      ),
    },
    {
      label: "Codes",
      href: "/codes",
      icon: (
        <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
        </svg>
      ),
    },
    ...(isCoach
      ? [
          {
            label: "Coach",
            href: "/coach",
            accent: true,
            icon: (
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            ),
          },
        ]
      : []),
  ];

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
        navItems={navItems}
        currentPath="/dashboard"
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
            userName={user?.full_name}
            userEmail={user?.email}
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
