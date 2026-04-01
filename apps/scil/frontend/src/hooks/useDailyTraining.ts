"use client";

import { useState, useEffect, useCallback } from "react";
import { api } from "@/lib/api";
import type {
  TodayTraining,
  TrainingPlanSummary,
  TrainingPlanDetail,
  TrainingStats,
  TrainingContentItem,
  TrainingDayProgress,
} from "@/lib/types";

export function useDailyTraining() {
  const [today, setToday] = useState<TodayTraining | null>(null);
  const [plans, setPlans] = useState<TrainingPlanSummary[]>([]);
  const [activePlan, setActivePlan] = useState<TrainingPlanDetail | null>(null);
  const [stats, setStats] = useState<TrainingStats | null>(null);
  const [contentLibrary, setContentLibrary] = useState<TrainingContentItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch today's training
  const fetchToday = useCallback(async () => {
    try {
      const data = await api.get<TodayTraining>("/training/today");
      setToday(data);
      if (data.stats) setStats(data.stats);
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Fehler beim Laden";
      setError(msg);
    }
  }, []);

  // Fetch all plans
  const fetchPlans = useCallback(async () => {
    try {
      const data = await api.get<TrainingPlanSummary[]>("/training/plans");
      setPlans(data);
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Fehler beim Laden";
      setError(msg);
    }
  }, []);

  // Fetch plan detail
  const fetchPlanDetail = useCallback(async (planId: string) => {
    try {
      const data = await api.get<TrainingPlanDetail>(`/training/plans/${planId}`);
      setActivePlan(data);
      return data;
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Fehler beim Laden";
      setError(msg);
      return null;
    }
  }, []);

  // Generate new plan
  const generatePlan = useCallback(async (resultId?: string, weeks?: number, daysPerWeek?: number) => {
    setError(null);
    try {
      const data = await api.post<TrainingPlanDetail>("/training/plans", {
        result_id: resultId || null,
        total_weeks: weeks || 4,
        days_per_week: daysPerWeek || 5,
      });
      setActivePlan(data);
      await fetchPlans();
      await fetchToday();
      return data;
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Fehler beim Erstellen";
      setError(msg);
      return null;
    }
  }, [fetchPlans, fetchToday]);

  // Start a training day
  const startDay = useCallback(async (dayId: string) => {
    setError(null);
    try {
      const data = await api.post<TrainingDayProgress>(`/training/days/${dayId}/start`);
      await fetchToday();
      return data;
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Fehler beim Starten";
      setError(msg);
      return null;
    }
  }, [fetchToday]);

  // Complete a training day
  const completeDay = useCallback(async (
    dayId: string,
    reflection?: string,
    rating?: number,
    answers?: Record<string, unknown>,
  ) => {
    setError(null);
    try {
      const data = await api.post<TrainingDayProgress>(`/training/days/${dayId}/complete`, {
        reflection: reflection || null,
        rating: rating || null,
        answers: answers || null,
      });
      await fetchToday();
      if (activePlan) {
        await fetchPlanDetail(activePlan.id);
      }
      return data;
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Fehler beim Abschliessen";
      setError(msg);
      return null;
    }
  }, [fetchToday, activePlan, fetchPlanDetail]);

  // Fetch stats
  const fetchStats = useCallback(async () => {
    try {
      const data = await api.get<TrainingStats>("/training/stats");
      setStats(data);
      return data;
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Fehler beim Laden";
      setError(msg);
      return null;
    }
  }, []);

  // Fetch content library
  const fetchContent = useCallback(async (area?: string) => {
    try {
      const path = area ? `/training/content?area=${area}` : "/training/content";
      const data = await api.get<TrainingContentItem[]>(path);
      setContentLibrary(data);
      return data;
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Fehler beim Laden";
      setError(msg);
      return [];
    }
  }, []);

  // Initial load
  useEffect(() => {
    setIsLoading(true);
    Promise.all([fetchToday(), fetchPlans()])
      .finally(() => setIsLoading(false));
  }, [fetchToday, fetchPlans]);

  return {
    today,
    plans,
    activePlan,
    stats,
    contentLibrary,
    isLoading,
    error,
    fetchToday,
    fetchPlans,
    fetchPlanDetail,
    generatePlan,
    startDay,
    completeDay,
    fetchStats,
    fetchContent,
  };
}
