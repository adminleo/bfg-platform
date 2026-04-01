"use client";

import { useState, useCallback, useEffect } from "react";
import { api } from "@/lib/api";
import type { Session, SessionDetail, DiagnosticResult } from "@/lib/types";

export function useSessions() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [activeSession, setActiveSession] = useState<SessionDetail | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const fetchSessions = useCallback(async () => {
    try {
      const data = await api.get<Session[]>("/scil/sessions");
      setSessions(data);
    } catch (e) {
      console.error("Failed to fetch sessions:", e);
    }
  }, []);

  const createSession = useCallback(async (title?: string): Promise<Session | null> => {
    setIsLoading(true);
    try {
      const session = await api.post<Session>("/scil/sessions", title ? { title } : {});
      setSessions((prev) => [session, ...prev]);
      setActiveSessionId(session.id);
      return session;
    } catch (e) {
      console.error("Failed to create session:", e);
      throw e;  // Re-throw for caller to handle (e.g., 402 Payment Required)
    } finally {
      setIsLoading(false);
    }
  }, []);

  const loadSession = useCallback(async (sessionId: string) => {
    setIsLoading(true);
    setActiveSessionId(sessionId);
    try {
      const detail = await api.get<SessionDetail>(`/scil/sessions/${sessionId}`);
      setActiveSession(detail);
    } catch (e) {
      console.error("Failed to load session:", e);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const renameSession = useCallback(async (sessionId: string, title: string) => {
    try {
      await api.patch(`/scil/sessions/${sessionId}`, { title });
      setSessions((prev) =>
        prev.map((s) => (s.id === sessionId ? { ...s, title } : s))
      );
    } catch (e) {
      console.error("Failed to rename session:", e);
    }
  }, []);

  const deleteSession = useCallback(async (sessionId: string) => {
    try {
      await api.delete(`/scil/sessions/${sessionId}`);
      setSessions((prev) => prev.filter((s) => s.id !== sessionId));
      if (activeSessionId === sessionId) {
        setActiveSessionId(null);
        setActiveSession(null);
      }
    } catch (e) {
      console.error("Failed to delete session:", e);
    }
  }, [activeSessionId]);

  const getResult = useCallback(async (sessionId: string): Promise<DiagnosticResult | null> => {
    try {
      return await api.get<DiagnosticResult>(`/scil/sessions/${sessionId}/result`);
    } catch (e) {
      console.error("Failed to get result:", e);
      return null;
    }
  }, []);

  // Load sessions on mount
  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

  return {
    sessions,
    activeSessionId,
    activeSession,
    isLoading,
    createSession,
    loadSession,
    renameSession,
    deleteSession,
    getResult,
    setActiveSessionId,
    fetchSessions,
  };
}
