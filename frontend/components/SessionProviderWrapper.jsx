// components/SessionProviderWrapper.jsx
"use client";

import React, { useEffect } from "react";
import { SessionProvider, useSession } from "next-auth/react";

function TokenSync() {
  const { data: session, status } = useSession();

  useEffect(() => {
    // Only sync token when session is fully loaded and authenticated
    if (status === "authenticated" && session?.user?.accessToken) {
      localStorage.setItem("token", session.user.accessToken);
      console.log("Token synced:", session.user.accessToken);
    } else if (status === "unauthenticated") {
      // Clear token when explicitly unauthenticated
      localStorage.removeItem("token");
    }
    // Don't do anything during "loading" state to avoid flashing
  }, [session, status]);

  return null;
}

export default function SessionProviderWrapper({ children }) {
  return (
    <SessionProvider>
      <TokenSync />
      {children}
    </SessionProvider>
  );
}
