// app/dashboard/page.js
"use client";

import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function DashboardPage() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [secureData, setSecureData] = useState(null);

  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/login");
    }
  }, [status, router]);

  useEffect(() => {
    if (status === "authenticated") {
      // Example: calling a protected route
      fetch("http://localhost:8000/protected-endpoint", {
        headers: {
          Authorization: `Bearer ${session?.user?.accessToken}`,
        },
      })
        .then((r) => r.json())
        .then((data) => setSecureData(data));
    }
  }, [status, session]);

  if (status === "loading") return <p>Loading...</p>;
  if (status === "unauthenticated") return null;

  return (
    <div>
      <h1>Dashboard</h1>
      <p>Welcome {session.user.email}!</p>
      <p>Secure Data: {JSON.stringify(secureData)}</p>
    </div>
  );
}
