// app/login/page.js
"use client";

// Import React, hooks, and Material UI components
import React, { useState, useEffect } from "react";
import { signIn, useSession } from "next-auth/react"; // NextAuth credential provider sign in
import { useRouter } from "next/navigation"; // For client-side navigation
import {
  Box,
  Button,
  TextField,
  Typography,
  FormControlLabel,
  Checkbox,
  CircularProgress
} from "@mui/material";

export default function LoginPage() {
  // Local state for toggling between sign in and sign up modes.
  const router = useRouter();
  const { data: session, status } = useSession();
  const [isSignUp, setIsSignUp] = useState(false);
  // Fields for email, password, and full name (for sign up)
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [errorMsg, setErrorMsg] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  
  // Redirect if user is already logged in
  useEffect(() => {
    if (status === "authenticated") {
      router.push("/historical");
    }
  }, [status, router]);

  // Toggle mode between sign up and sign in
  const toggleMode = () => {
    setIsSignUp(!isSignUp);
    setErrorMsg(null);
    setEmail("");
    setPassword("");
    setFullName("");
  };

  // Handle user registration. Calls your backend /users/signup endpoint.
  const handleSignUp = async () => {
    setErrorMsg(null);
    setIsLoading(true);
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/v1/users/signup`, {
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
      setIsLoading(false);
    }
  };

  // Handle user sign in using NextAuth credentials provider.
  const handleSignIn = async () => {
    setErrorMsg(null);
    setIsLoading(true);
    try {
      const result = await signIn("credentials", {
        redirect: false,
        email,
        password,
      });
      if (result?.error) {
        setErrorMsg(result.error);
        setIsLoading(false);
      } else {
        router.push("/historical");
      }
    } catch (err) {
      setErrorMsg("An unexpected error occurred. Please try again.");
      setIsLoading(false);
    }
  };

  // Submit handler chooses sign up vs. sign in based on mode.
  const handleSubmit = (e) => {
    e.preventDefault();
    if (isSignUp) handleSignUp();
    else handleSignIn();
  };

  // If loading or already authenticated, show loading spinner
  if (status === "loading" || status === "authenticated") {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box
      component="form"
      onSubmit={handleSubmit}
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
          autoFocus={isSignUp}
        />
      )}

      <TextField
        label="Email"
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
        autoFocus={!isSignUp}
      />
      <TextField
        label="Password"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
        onKeyDown={(e) => {
          if (e.key === 'Enter') {
            handleSubmit(e);
          }
        }}
      />

      {errorMsg && (
        <Typography variant="body2" color="error">
          {errorMsg}
        </Typography>
      )}

      <Button 
        variant="contained" 
        type="submit"
        disabled={isLoading}
      >
        {isLoading ? (
          <CircularProgress size={24} />
        ) : (
          isSignUp ? "Sign Up" : "Sign In"
        )}
      </Button>

      <Button variant="text" onClick={toggleMode} disabled={isLoading}>
        {isSignUp
          ? "Already have an account? Sign In"
          : "Don't have an account? Sign Up"}
      </Button>
    </Box>
  );
}
