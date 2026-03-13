"use client";

import { RoleGuard } from "@/components/auth/RoleGuard";

export default function CoachLayout({ children }: { children: React.ReactNode }) {
  return (
    <RoleGuard allowedRoles={["coach", "admin"]}>
      {children}
    </RoleGuard>
  );
}
