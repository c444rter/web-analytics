"use client";

import React from "react";
import Button from "@mui/material/Button";
import Typography from "@mui/material/Typography";

export default function HomePage() {
  return (
    <main style={{ padding: "2rem" }}>
      <Typography variant="h4" gutterBottom>
        Welcome to Your Next.js App
      </Typography>
      <Typography variant="body1">
        This is the home page. From here, navigate to /upload or /dashboard.
      </Typography>
      <div style={{ marginTop: "1rem" }}>
        <Button
          variant="contained"
          href="/upload"
          style={{ marginRight: "1rem" }}
        >
          Go to Upload
        </Button>
        <Button variant="outlined" href="/dashboard">
          Go to Dashboard
        </Button>
      </div>
    </main>
  );
}
