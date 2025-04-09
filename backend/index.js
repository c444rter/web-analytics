// app/index.js
"use client";

import React from "react";
import { Box, Typography, Button } from "@mui/material";
import { useRouter } from "next/navigation";

export default function HomePage() {
  const router = useRouter();

  return (
    <Box sx={{ p: 4, textAlign: "center" }}>
      <Typography variant="h3" gutterBottom>
        Welcome to My Shopify Analytics App!
      </Typography>
      <Typography variant="body1" gutterBottom>
        Use the navigation bar above or the links below to explore your analytics.
      </Typography>
      <Box sx={{ mt: 4 }}>
        <Button variant="contained" onClick={() => router.push("/dashboard")}>
          Go to Dashboard
        </Button>
        <Button variant="outlined" onClick={() => router.push("/upload")} sx={{ ml: 2 }}>
          Upload File
        </Button>
      </Box>
    </Box>
  );
}
