"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      router.replace("/dashboard");
    } else {
      router.replace("/login");
    }
  }, [router]);

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="flex gap-1">
        <div className="w-2 h-2 rounded-full bg-scil typing-dot" />
        <div className="w-2 h-2 rounded-full bg-scil typing-dot" />
        <div className="w-2 h-2 rounded-full bg-scil typing-dot" />
      </div>
    </div>
  );
}
