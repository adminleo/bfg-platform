"use client";

import { useState, useEffect, useCallback } from "react";
import { api } from "@/lib/api";
import type {
  CoachDashboardStats,
  CoacheeListItem,
  CoacheeDetail,
  CodeInventoryItem,
  ActivityItem,
  InviteResponse,
} from "@/lib/types";

export function useCoachDashboard() {
  const [stats, setStats] = useState<CoachDashboardStats | null>(null);
  const [coachees, setCoachees] = useState<CoacheeListItem[]>([]);
  const [codes, setCodes] = useState<CodeInventoryItem[]>([]);
  const [activity, setActivity] = useState<ActivityItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboard = useCallback(async () => {
    try {
      const data = await api.get<CoachDashboardStats>("/coach/dashboard");
      setStats(data);
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Fehler beim Laden";
      setError(msg);
    }
  }, []);

  const fetchCoachees = useCallback(async () => {
    try {
      const data = await api.get<CoacheeListItem[]>("/coach/coachees");
      setCoachees(data);
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Fehler beim Laden";
      setError(msg);
    }
  }, []);

  const fetchCoacheeDetail = useCallback(async (id: string): Promise<CoacheeDetail | null> => {
    try {
      return await api.get<CoacheeDetail>(`/coach/coachees/${id}`);
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Fehler beim Laden";
      setError(msg);
      return null;
    }
  }, []);

  const fetchCodes = useCallback(async () => {
    try {
      const data = await api.get<CodeInventoryItem[]>("/coach/codes");
      setCodes(data);
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Fehler beim Laden";
      setError(msg);
    }
  }, []);

  const fetchActivity = useCallback(async () => {
    try {
      const data = await api.get<ActivityItem[]>("/coach/activity");
      setActivity(data);
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Fehler beim Laden";
      setError(msg);
    }
  }, []);

  const inviteCoachee = useCallback(async (
    email: string,
    notes?: string,
    tokenId?: string,
  ): Promise<InviteResponse | null> => {
    setError(null);
    try {
      const body: Record<string, unknown> = { email };
      if (notes) body.notes = notes;
      if (tokenId) body.token_id = tokenId;
      const result = await api.post<InviteResponse>("/coach/invite", body);
      // Refresh lists
      await Promise.all([fetchCoachees(), fetchDashboard(), fetchCodes()]);
      return result;
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Einladung fehlgeschlagen";
      setError(msg);
      return null;
    }
  }, [fetchCoachees, fetchDashboard, fetchCodes]);

  const assignCode = useCallback(async (
    assignmentId: string,
    tokenId: string,
  ): Promise<boolean> => {
    setError(null);
    try {
      await api.post("/coach/codes/assign", {
        assignment_id: assignmentId,
        token_id: tokenId,
      });
      await Promise.all([fetchCoachees(), fetchCodes()]);
      return true;
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Zuweisung fehlgeschlagen";
      setError(msg);
      return false;
    }
  }, [fetchCoachees, fetchCodes]);

  // Load all data on mount
  useEffect(() => {
    setIsLoading(true);
    Promise.all([
      fetchDashboard(),
      fetchCoachees(),
      fetchCodes(),
      fetchActivity(),
    ]).finally(() => setIsLoading(false));
  }, [fetchDashboard, fetchCoachees, fetchCodes, fetchActivity]);

  return {
    stats,
    coachees,
    codes,
    activity,
    isLoading,
    error,
    fetchDashboard,
    fetchCoachees,
    fetchCoacheeDetail,
    fetchCodes,
    fetchActivity,
    inviteCoachee,
    assignCode,
  };
}
