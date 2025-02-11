"use client";

import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function AdminPage() {
  const { data: session, status } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (status === "unauthenticated") {
      // If not logged in, redirect
      router.push("/login");
    }
    // Optionally, check if session.user has 'admin' role
    // if (status === "authenticated" && !session.user.isAdmin) {
    //   router.push("/"); // or show 403 page
    // }
  }, [status, router]);

  if (status === "loading") return <p>Loading...</p>;
  return (
    <div>
      <h1>Admin Dashboard</h1>
      <p>Welcome, {session?.user?.email}</p>
      <ul>
        <li>
          <a href="/admin/whitelist">Manage Whitelist</a>
        </li>
        {/* add more admin links */}
      </ul>
    </div>
  );
}
