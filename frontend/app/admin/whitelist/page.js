"use client";

import { useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";

export default function WhitelistAdminPage() {
  const [whitelist, setWhitelist] = useState([]);
  const [newEmail, setNewEmail] = useState("");
  const { data: session, status } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/login");
    }
    // If you store an isAdmin flag in session, check it here
  }, [status, router]);

  useEffect(() => {
    // Fetch current whitelist from FastAPI
    fetch("http://localhost:8000/admin/whitelist")
      .then((res) => res.json())
      .then((data) => setWhitelist(data));
  }, []);

  const handleAdd = async () => {
    const res = await fetch("http://localhost:8000/admin/whitelist", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: newEmail }),
    });
    if (res.ok) {
      const updated = await res.json();
      setWhitelist(updated);
      setNewEmail("");
    }
  };

  if (status === "loading") return <p>Loading...</p>;

  return (
    <div>
      <h1>Whitelist Admin</h1>
      <ul>
        {whitelist.map((em) => (
          <li key={em}>{em}</li>
        ))}
      </ul>
      <input
        type="email"
        value={newEmail}
        onChange={(e) => setNewEmail(e.target.value)}
        placeholder="Add email to whitelist"
      />
      <button onClick={handleAdd}>Add</button>
    </div>
  );
}
