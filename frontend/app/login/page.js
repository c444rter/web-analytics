// app/login/page.js
"use client";

// Import React, hooks, and Material UI components
import React, { useState } from "react";
import { signIn } from "next-auth/react"; // NextAuth credential provider sign in
import { useRouter } from "next/navigation"; // For client-side navigation
import {
  Box,
  Button,
  TextField,
  Typography,
  FormControlLabel,
  Checkbox
} from "@mui/material";

export default function LoginPage() {
  // Local state for toggling between sign in and sign up modes.
  const router = useRouter();
  const [isSignUp, setIsSignUp] = useState(false);
  // Fields for email, password, and full name (for sign up)
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [rememberMe, setRememberMe] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  // Toggle mode between sign up and sign in
  const toggleMode = () => {
    setIsSignUp(!isSignUp);
    setErrorMsg(null);
    setEmail("");
    setPassword("");
    setFullName("");
    setRememberMe(false);
  };

  // Handle user registration. Calls your backend /users/signup endpoint.
  const handleSignUp = async () => {
    setErrorMsg(null);
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/users/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password, username: fullName }),
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Registration failed");
      }
      // On successful registration, sign in automatically.
      await handleSignIn();
    } catch (err) {
      setErrorMsg(err.message);
    }
  };

  // Handle user sign in using NextAuth credentials provider.
  const handleSignIn = async () => {
    setErrorMsg(null);
    const result = await signIn("credentials", {
      redirect: false,
      email,
      password,
      rememberMe,
    });
    if (result?.error) {
      setErrorMsg(result.error);
    } else {
      // On success, navigate to your dashboard.
      router.push("/historical");
    }
  };

  // Submit handler chooses sign up vs. sign in based on mode.
  const handleSubmit = (e) => {
    e.preventDefault();
    if (isSignUp) handleSignUp();
    else handleSignIn();
  };

  return (
    <Box
      sx={{
        maxWidth: 400,
        margin: "0 auto",
        padding: 4,
        display: "flex",
        flexDirection: "column",
        gap: 2,
        border: "1px solid #ccc",
        borderRadius: 2,
      }}
    >
      <Typography variant="h5" textAlign="center">
        {isSignUp ? "Create an Account" : "Sign In"}
      </Typography>

      {isSignUp && (
        <TextField
          label="Full Name"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
          required
        />
      )}

      <TextField
        label="Email"
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
      />
      <TextField
        label="Password"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
      />

      <FormControlLabel
        control={
          <Checkbox
            checked={rememberMe}
            onChange={(e) => setRememberMe(e.target.checked)}
          />
        }
        label="Remember Me"
      />

      {errorMsg && (
        <Typography variant="body2" color="error">
          {errorMsg}
        </Typography>
      )}

      <Button variant="contained" onClick={handleSubmit}>
        {isSignUp ? "Sign Up" : "Sign In"}
      </Button>

      <Button variant="text" onClick={toggleMode}>
        {isSignUp
          ? "Already have an account? Sign In"
          : "Don't have an account? Sign Up"}
      </Button>
    </Box>
  );
}
