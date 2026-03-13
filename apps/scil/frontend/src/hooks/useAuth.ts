"use client";

import { useState, useEffect, useCallback } from "react";
import { api } from "@/lib/api";
import type { AuthToken, UserData } from "@/lib/types";

export function useAuth() {
  const [user, setUser] = useState<UserData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const isAuthenticated = !!user;

  useEffect(() => {
    // Check for existing token
    const token = localStorage.getItem("access_token");
    if (token) {
      // Validate token by fetching user (simple approach)
      setUser(JSON.parse(localStorage.getItem("user_data") || "null"));
    }
    setIsLoading(false);
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    setError(null);
    try {
      const formData = new URLSearchParams();
      formData.append("username", email);
      formData.append("password", password);

      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/auth/login`,
        {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body: formData.toString(),
        }
      );

      if (!res.ok) {
        const data = await res.json().catch(() => ({ detail: "Login fehlgeschlagen" }));
        throw new Error(data.detail || "Login fehlgeschlagen");
      }

      const token: AuthToken = await res.json();
      localStorage.setItem("access_token", token.access_token);

      // Decode JWT to get user info (simple base64 decode)
      const payload = JSON.parse(atob(token.access_token.split(".")[1]));
      const userData: UserData = {
        id: payload.sub,
        email: payload.email || email,
        full_name: payload.full_name || email,
        role: payload.role || "trainee",
      };
      localStorage.setItem("user_data", JSON.stringify(userData));
      setUser(userData);

      return true;
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Login fehlgeschlagen";
      setError(msg);
      return false;
    }
  }, []);

  const register = useCallback(async (email: string, password: string, fullName: string) => {
    setError(null);
    try {
      await api.post("/auth/register", { email, password, full_name: fullName });

      // Auto-login after registration
      return await login(email, password);
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Registrierung fehlgeschlagen";
      setError(msg);
      return false;
    }
  }, [login]);

  const logout = useCallback(() => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user_data");
    setUser(null);
  }, []);

  const isCoach = user?.role === "coach" || user?.role === "admin";

  return { user, isAuthenticated, isCoach, isLoading, error, login, register, logout };
}
