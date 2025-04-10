// components/SessionProviderWrapper.jsx
"use client";

import React, { useEffect } from "react";
import { SessionProvider, useSession } from "next-auth/react";

function TokenSync() {
  const { data: session } = useSession();

  useEffect(() => {
    if (session && session.user && session.user.accessToken) {
      localStorage.setItem("token", session.user.accessToken);
      console.log("Token synced:", session.user.accessToken);
    } else {
      // Optionally, if the session is removed, clear the token.
      localStorage.removeItem("token");
    }
  }, [session]);

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
