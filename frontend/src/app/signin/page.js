"use client";

import { signIn } from "next-auth/react";
import React, { useState } from "react";

export default function SignInPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    // NextAuth "signIn" function with credentials
    const result = await signIn("credentials", {
      redirect: false, // we'll handle redirect manually
      email,
      password,
    });

    if (result.error) {
      setError("Invalid credentials");
    } else {
      // If success, redirect or do something
      window.location.href = "/dashboard"; 
    }
  };

  return (
    <div style={{ maxWidth: "400px", margin: "2rem auto" }}>
      <h1>Sign In</h1>
      <form onSubmit={handleSubmit}>
        <label>Email</label>
        <input
          type="text"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          style={{ display: "block", marginBottom: "1rem" }}
        />

        <label>Password</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={{ display: "block", marginBottom: "1rem" }}
        />

        <button type="submit" style={{ marginBottom: "1rem" }}>Sign In</button>
      </form>
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}
