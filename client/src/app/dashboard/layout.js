"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { isAuthenticated } from "@/utils/auth";
import Navbar from "@/components/common/Navbar";

export default function DashboardTemplate({ children }) {
  const router = useRouter();
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.replace("/"); // Redirect
    } else {
      setChecking(false); // Only allow children to render if authenticated
    }
  }, [router]);

  if (checking) {
    return null; // or show a loading spinner
  }

  return (
    <div className="bg-white">
      <Navbar />
      {children}
    </div>
  );
}
