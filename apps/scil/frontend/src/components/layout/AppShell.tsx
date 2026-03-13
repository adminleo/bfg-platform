"use client";

import { useEffect, ReactNode } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { ThreePanelLayout } from "./ThreePanelLayout";
import { SidebarShell } from "./SidebarShell";
import { getNavItems } from "@/lib/navigation";

interface AppShellProps {
  /** Page-specific content for the left sidebar (inside SidebarShell) */
  leftSidebar: ReactNode;
  /** Main center content */
  children: ReactNode;
  /** Optional page-specific content for the right sidebar */
  rightSidebar?: ReactNode;
  /** Optional custom left sidebar header (e.g., SCIL branding + new diagnostic btn) */
  leftHeader?: ReactNode;
  /** Whether the right sidebar starts open (defaults to true if rightSidebar provided) */
  rightDefaultOpen?: boolean;
}

export function AppShell({
  leftSidebar,
  children,
  rightSidebar,
  leftHeader,
  rightDefaultOpen,
}: AppShellProps) {
  const router = useRouter();
  const pathname = usePathname();
  const { user, isAuthenticated, isLoading, logout } = useAuth();

  // Centralized auth guard
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.replace("/login");
    }
  }, [isLoading, isAuthenticated, router]);

  const handleLogout = () => {
    logout();
    router.replace("/login");
  };

  if (isLoading) {
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

  const navItems = getNavItems(user?.role);

  return (
    <ThreePanelLayout
      navItems={navItems}
      currentPath={pathname}
      rightDefaultOpen={rightDefaultOpen ?? !!rightSidebar}
      left={
        <SidebarShell
          userName={user?.full_name}
          userEmail={user?.email}
          onLogout={handleLogout}
          header={leftHeader}
        >
          {leftSidebar}
        </SidebarShell>
      }
      center={children}
      right={
        rightSidebar || (
          <div className="h-full bg-surface-dark" />
        )
      }
    />
  );
}
