"use client";

import React, { useState } from "react";

export default function HomePage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errorMsg, setErrorMsg] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg(null);

    try {
      const res = await fetch("http://localhost:8000/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      if (res.ok) {
        const data = await res.json();
        console.log("Login success:", data);

        // Example: store token in localStorage
        localStorage.setItem("token", data.token);

        // You might redirect to /dashboard
        window.location.href = "/dashboard";
      } else {
        const errData = await res.json();
        setErrorMsg(errData.detail || "Login failed");
      }
    } catch (err) {
      console.error("Login error:", err);
      setErrorMsg("An unexpected error occurred.");
    }
  };

  return (
    <main style={{ maxWidth: 400, margin: "0 auto", padding: "2rem" }}>
      <h1>Login</h1>
      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column" }}>
        <label>Email:</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          style={{ marginBottom: "1rem" }}
        />

        <label>Password:</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          style={{ marginBottom: "1rem" }}
        />

        <button type="submit" style={{ marginBottom: "1rem" }}>Log In</button>
      </form>

      {errorMsg && <p style={{ color: "red" }}>{errorMsg}</p>}
    </main>
  );
}
