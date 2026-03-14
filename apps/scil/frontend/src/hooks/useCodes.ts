"use client";

import { useState, useCallback, useEffect } from "react";
import { api } from "@/lib/api";
import type { DiagnosticCode, CodePackage, CheckoutResponse, Purchase } from "@/lib/types";

interface UseCodesReturn {
  codes: DiagnosticCode[];
  packages: CodePackage[];
  isLoading: boolean;
  error: string | null;
  hasActiveCode: boolean;
  purchasePackage: (packageType: string) => Promise<void>;
  devPurchase: (packageType: string) => Promise<Purchase | null>;
  redeemCode: (code: string) => Promise<{ success: boolean; message: string }>;
  activateCode: (codeId: string) => Promise<{ success: boolean; message: string }>;
  fetchCodes: () => Promise<void>;
  fetchPackages: () => Promise<void>;
  getPurchase: (purchaseId: string) => Promise<Purchase | null>;
}

export function useCodes(): UseCodesReturn {
  const [codes, setCodes] = useState<DiagnosticCode[]>([]);
  const [packages, setPackages] = useState<CodePackage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const hasActiveCode = codes.some((c) => c.status === "activated");

  const fetchPackages = useCallback(async () => {
    try {
      const data = await api.get<CodePackage[]>("/codes/packages");
      setPackages(data);
    } catch (e) {
      console.error("Failed to fetch packages:", e);
    }
  }, []);

  const fetchCodes = useCallback(async () => {
    try {
      const data = await api.get<DiagnosticCode[]>("/codes/my-codes");
      setCodes(data);
    } catch (e) {
      console.error("Failed to fetch codes:", e);
    }
  }, []);

  const purchasePackage = useCallback(async (packageType: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await api.post<CheckoutResponse>("/codes/purchase", {
        package_type: packageType,
      });
      // Redirect to Stripe Checkout
      if (response.checkout_url) {
        window.location.href = response.checkout_url;
      }
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Fehler beim Kauf";
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const devPurchase = useCallback(async (packageType: string): Promise<Purchase | null> => {
    setIsLoading(true);
    setError(null);
    try {
      const purchase = await api.post<Purchase>("/codes/dev-purchase", {
        package_type: packageType,
      });
      await fetchCodes();
      return purchase;
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Fehler beim Dev-Kauf";
      setError(msg);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [fetchCodes]);

  const redeemCode = useCallback(async (code: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await api.post<{ status: string; message: string }>("/codes/redeem", {
        code,
      });
      await fetchCodes();
      return { success: true, message: result.message };
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Code konnte nicht eingeloest werden";
      setError(msg);
      return { success: false, message: msg };
    } finally {
      setIsLoading(false);
    }
  }, [fetchCodes]);

  const activateCode = useCallback(async (codeId: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await api.post<{ status: string; message: string }>(`/codes/activate/${codeId}`, {});
      await fetchCodes();
      return { success: true, message: result.message };
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Code konnte nicht aktiviert werden";
      setError(msg);
      return { success: false, message: msg };
    } finally {
      setIsLoading(false);
    }
  }, [fetchCodes]);

  const getPurchase = useCallback(async (purchaseId: string): Promise<Purchase | null> => {
    try {
      return await api.get<Purchase>(`/codes/purchase/${purchaseId}`);
    } catch {
      return null;
    }
  }, []);

  useEffect(() => {
    fetchPackages();
    fetchCodes();
  }, [fetchPackages, fetchCodes]);

  return {
    codes,
    packages,
    isLoading,
    error,
    hasActiveCode,
    purchasePackage,
    devPurchase,
    redeemCode,
    activateCode,
    fetchCodes,
    fetchPackages,
    getPurchase,
  };
}
