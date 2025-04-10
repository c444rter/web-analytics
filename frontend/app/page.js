// app/page.js
"use client";

import { Box, Typography, Button } from "@mui/material";
import { useRouter } from "next/navigation";

export default function HomePage() {
  const router = useRouter();

  return (
    <Box sx={{ p: 4, textAlign: "center" }}>
      <Typography variant="h3" gutterBottom>
        DAVIDS
      </Typography>
      <Button variant="contained" onClick={() => router.push("/dashboard")}>
        Go to Dashboard
      </Button>
    </Box>
  );
}
