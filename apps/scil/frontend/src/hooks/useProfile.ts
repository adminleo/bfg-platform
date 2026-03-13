"use client";

import { useState, useEffect, useCallback } from "react";
import { api } from "@/lib/api";

interface Profile {
  id: string;
  email: string;
  full_name: string;
  role: string;
  bio: string | null;
  created_at: string;
}

interface CoachInfo {
  coach_name: string;
  coach_email: string;
  assignment_status: string;
  assigned_at: string;
}

interface HistoryItem {
  id: string;
  status: string;
  progress: number;
  started_at: string;
  completed_at: string | null;
  scores: Record<string, unknown> | null;
  polygon_data: Record<string, unknown> | null;
}

export function useProfile() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [coach, setCoach] = useState<CoachInfo | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchProfile = useCallback(async () => {
    try {
      const data = await api.get<Profile>("/me");
      setProfile(data);
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Fehler beim Laden";
      setError(msg);
    }
  }, []);

  const updateProfile = useCallback(async (updates: { full_name?: string; bio?: string }) => {
    setError(null);
    try {
      const data = await api.patch<Profile>("/me", updates);
      setProfile(data);
      return true;
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Fehler beim Speichern";
      setError(msg);
      return false;
    }
  }, []);

  const changePassword = useCallback(async (currentPassword: string, newPassword: string) => {
    setError(null);
    try {
      await api.post("/me/password", {
        current_password: currentPassword,
        new_password: newPassword,
      });
      return true;
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Fehler beim Aendern";
      setError(msg);
      return false;
    }
  }, []);

  const fetchCoach = useCallback(async () => {
    try {
      const data = await api.get<CoachInfo | null>("/me/coach");
      setCoach(data);
    } catch {
      // No coach assigned — that's fine
      setCoach(null);
    }
  }, []);

  const fetchHistory = useCallback(async () => {
    try {
      const data = await api.get<HistoryItem[]>("/me/history");
      setHistory(data);
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Fehler beim Laden";
      setError(msg);
    }
  }, []);

  useEffect(() => {
    setIsLoading(true);
    Promise.all([fetchProfile(), fetchCoach(), fetchHistory()])
      .finally(() => setIsLoading(false));
  }, [fetchProfile, fetchCoach, fetchHistory]);

  return {
    profile,
    coach,
    history,
    isLoading,
    error,
    fetchProfile,
    updateProfile,
    changePassword,
    fetchCoach,
    fetchHistory,
  };
}
