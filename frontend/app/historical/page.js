// app/historical/page.jsx

"use client";

import React, { useEffect } from "react";
import { Box, Typography, CircularProgress } from "@mui/material";
import { useRouter } from "next/navigation";
import useHistoricalUploads from "../../hooks/useHistoricalUploads"; // ensure this hook exists
import { useSession } from "next-auth/react";

export default function HistoricalPage() {
  const router = useRouter();
  const { data: session, status } = useSession();
  const { data: uploads, isLoading, isError } = useHistoricalUploads(); // fetch historical uploads

  // If not authenticated, redirect outside render.
  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/login");
    }
  }, [status, router]);

  if (isLoading) {
    return (
      <Box sx={{ p: 3 }}>
        <CircularProgress />
        <Typography>Loading historical uploads...</Typography>
      </Box>
    );
  }

  if (isError) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography color="error">Error fetching historical uploads.</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" mb={2}>
        Historical Uploads
      </Typography>
      {uploads && uploads.length > 0 ? (
        uploads.map((upload) => (
          <Box key={upload.id} sx={{ mb: 2, p: 2, border: "1px solid #ccc", borderRadius: 1 }}>
            <Typography variant="subtitle1">
              {upload.file_name} (Uploaded: {new Date(upload.uploaded_at).toLocaleString()})
            </Typography>
            <Typography>Status: {upload.status}</Typography>
          </Box>
        ))
      ) : (
        <Typography>No uploads found.</Typography>
      )}
    </Box>
  );
}
