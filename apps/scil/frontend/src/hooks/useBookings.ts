"use client";

import { useState, useEffect, useCallback } from "react";
import type {
  AvailabilitySlot,
  AvailableTime,
  Booking,
  SessionBriefing,
} from "@/lib/types";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

function authHeaders(): Record<string, string> {
  const token =
    typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export function useBookings() {
  // ── State ───────────────────────────────────────────────────────────
  const [slots, setSlots] = useState<AvailabilitySlot[]>([]);
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [upcomingBookings, setUpcomingBookings] = useState<Booking[]>([]);
  const [availableTimes, setAvailableTimes] = useState<AvailableTime[]>([]);
  const [currentBriefing, setCurrentBriefing] = useState<SessionBriefing | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // ── Helpers ─────────────────────────────────────────────────────────
  const clearError = () => setError(null);

  async function apiFetch<T>(
    url: string,
    options?: RequestInit
  ): Promise<T> {
    const res = await fetch(`${API}${url}`, {
      headers: {
        "Content-Type": "application/json",
        ...authHeaders(),
      },
      ...options,
    });
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      throw new Error(body.detail || `HTTP ${res.status}`);
    }
    if (res.status === 204) return undefined as unknown as T;
    return res.json();
  }

  // ── Coach: Slots ────────────────────────────────────────────────────
  const fetchSlots = useCallback(async () => {
    try {
      const data = await apiFetch<AvailabilitySlot[]>("/bookings/slots");
      setSlots(data);
    } catch {
      // Silently ignore — user may not be a coach
    }
  }, []);

  const createSlot = useCallback(
    async (slot: {
      day_of_week: number;
      start_time: string;
      end_time: string;
      duration_minutes?: number;
      recurrence?: string;
      notes?: string;
    }) => {
      setError(null);
      const data = await apiFetch<AvailabilitySlot>("/bookings/slots", {
        method: "POST",
        body: JSON.stringify(slot),
      });
      setSlots((prev) => [...prev, data]);
      return data;
    },
    []
  );

  const updateSlot = useCallback(
    async (
      slotId: string,
      updates: Partial<{
        start_time: string;
        end_time: string;
        duration_minutes: number;
        recurrence: string;
        notes: string;
        is_active: boolean;
      }>
    ) => {
      setError(null);
      const data = await apiFetch<AvailabilitySlot>(
        `/bookings/slots/${slotId}`,
        { method: "PATCH", body: JSON.stringify(updates) }
      );
      setSlots((prev) => prev.map((s) => (s.id === slotId ? data : s)));
      return data;
    },
    []
  );

  const deleteSlot = useCallback(async (slotId: string) => {
    setError(null);
    await apiFetch<void>(`/bookings/slots/${slotId}`, { method: "DELETE" });
    setSlots((prev) => prev.filter((s) => s.id !== slotId));
  }, []);

  // ── Coachee: Available Times ────────────────────────────────────────
  const fetchAvailableTimes = useCallback(
    async (coachId: string, startDate: string, endDate: string) => {
      setError(null);
      const params = new URLSearchParams({ start_date: startDate, end_date: endDate });
      const data = await apiFetch<AvailableTime[]>(
        `/bookings/available/${coachId}?${params}`
      );
      setAvailableTimes(data);
      return data;
    },
    []
  );

  // ── Bookings CRUD ───────────────────────────────────────────────────
  const fetchBookings = useCallback(
    async (role?: string, status?: string) => {
      setIsLoading(true);
      setError(null);
      try {
        const params = new URLSearchParams();
        if (role) params.set("role", role);
        if (status) params.set("status_filter", status);
        const query = params.toString() ? `?${params}` : "";
        const data = await apiFetch<Booking[]>(`/bookings${query}`);
        setBookings(data);
        return data;
      } catch (e) {
        setError(e instanceof Error ? e.message : "Fehler beim Laden der Buchungen");
        return [];
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const fetchUpcoming = useCallback(async (limit = 5) => {
    try {
      const data = await apiFetch<Booking[]>(
        `/bookings/upcoming?limit=${limit}`
      );
      setUpcomingBookings(data);
      return data;
    } catch {
      return [];
    }
  }, []);

  const createBooking = useCallback(
    async (booking: {
      coach_id: string;
      scheduled_at: string;
      topic?: string;
      coachee_notes?: string;
      slot_id?: string;
    }) => {
      setError(null);
      const data = await apiFetch<Booking>("/bookings", {
        method: "POST",
        body: JSON.stringify(booking),
      });
      setBookings((prev) => [data, ...prev]);
      return data;
    },
    []
  );

  const getBooking = useCallback(async (bookingId: string) => {
    return apiFetch<Booking>(`/bookings/${bookingId}`);
  }, []);

  const confirmBooking = useCallback(async (bookingId: string) => {
    setError(null);
    const data = await apiFetch<Booking>(`/bookings/${bookingId}/confirm`, {
      method: "POST",
    });
    setBookings((prev) => prev.map((b) => (b.id === bookingId ? data : b)));
    return data;
  }, []);

  const cancelBooking = useCallback(async (bookingId: string) => {
    setError(null);
    const data = await apiFetch<Booking>(`/bookings/${bookingId}/cancel`, {
      method: "POST",
    });
    setBookings((prev) => prev.map((b) => (b.id === bookingId ? data : b)));
    return data;
  }, []);

  const completeBooking = useCallback(
    async (
      bookingId: string,
      notes?: { coach_notes?: string; summary?: string }
    ) => {
      setError(null);
      const data = await apiFetch<Booking>(`/bookings/${bookingId}/complete`, {
        method: "POST",
        body: JSON.stringify(notes ?? {}),
      });
      setBookings((prev) => prev.map((b) => (b.id === bookingId ? data : b)));
      return data;
    },
    []
  );

  // ── Briefing ────────────────────────────────────────────────────────
  const fetchBriefing = useCallback(async (bookingId: string) => {
    setError(null);
    const data = await apiFetch<SessionBriefing>(
      `/bookings/${bookingId}/briefing`
    );
    setCurrentBriefing(data);
    return data;
  }, []);

  const regenerateBriefing = useCallback(async (bookingId: string) => {
    setError(null);
    const data = await apiFetch<SessionBriefing>(
      `/bookings/${bookingId}/briefing/regenerate`,
      { method: "POST" }
    );
    setCurrentBriefing(data);
    return data;
  }, []);

  // ── Auto-fetch on mount ─────────────────────────────────────────────
  useEffect(() => {
    fetchBookings();
    fetchUpcoming();
    fetchSlots();
  }, [fetchBookings, fetchUpcoming, fetchSlots]);

  return {
    // State
    slots,
    bookings,
    upcomingBookings,
    availableTimes,
    currentBriefing,
    isLoading,
    error,
    clearError,
    // Coach: Slots
    fetchSlots,
    createSlot,
    updateSlot,
    deleteSlot,
    // Available times
    fetchAvailableTimes,
    // Bookings
    fetchBookings,
    fetchUpcoming,
    createBooking,
    getBooking,
    confirmBooking,
    cancelBooking,
    completeBooking,
    // Briefing
    fetchBriefing,
    regenerateBriefing,
  };
}
