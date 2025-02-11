// app/login/page.js
"use client";

import { useState } from "react";
import { signIn } from "next-auth/react";
import { useRouter } from "next/navigation";
import {
  Box,
  Button,
  TextField,
  Typography,
  FormControlLabel,
  Checkbox,
} from "@mui/material";

export default function LoginPage() {
  const router = useRouter();
  const [isSignUp, setIsSignUp] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [rememberMe, setRememberMe] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  const toggleMode = () => {
    setIsSignUp(!isSignUp);
    setErrorMsg(null);
    setEmail("");
    setPassword("");
    setFullName("");
    setRememberMe(false);
  };

  const handleSignUp = async () => {
    setErrorMsg(null);
    try {
      // Basic register call, adjust to your actual endpoint
      const res = await fetch("http://localhost:8000/users/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password, full_name: fullName }),
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Registration failed");
      }
      // Registration succeeded, auto sign in
      await handleSignIn();
    } catch (err) {
      setErrorMsg(err.message);
    }
  };

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
      router.push("/dashboard");
    }
  };

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
