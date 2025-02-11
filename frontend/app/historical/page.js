// app/historical/page.js
"use client";

import React, { useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import {
  Box,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Paper,
  Button,
} from "@mui/material";

export default function HistoricalPage() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [uploads, setUploads] = useState([]);

  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/login");
    }
  }, [status, router]);

  useEffect(() => {
    if (status === "authenticated") {
      fetch("http://localhost:8000/uploads/history", {
        headers: {
          Authorization: `Bearer ${session?.user?.accessToken}`,
        },
      })
        .then((r) => r.json())
        .then((data) => {
          // if API returns an array
          if (Array.isArray(data)) {
            setUploads(data);
          } else {
            // if it returns { uploads: [...] }
            setUploads(data?.uploads || []);
          }
        })
        .catch((err) => {
          console.error("Fetch error:", err);
          setUploads([]);
        });
    }
  }, [status, session]);

  if (status === "loading") return <p>Loading...</p>;
  if (status === "unauthenticated") return null;

  const handleGoToUpload = () => {
    router.push("/upload");
  };

  if (uploads.length === 0) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" mb={2}>
          No Historical Data
        </Typography>
        <Typography variant="body1" mb={2}>
          You haven’t uploaded anything yet. Click below to upload now!
        </Typography>
        <Button variant="contained" onClick={handleGoToUpload}>
          Go to Upload Page
        </Button>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" mb={2}>
        Historical Uploads
      </Typography>
      <Paper>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>File Name</TableCell>
              <TableCell>Size in Rows</TableCell>
              <TableCell>Size in MB</TableCell>
              <TableCell>Date Uploaded</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {uploads.map((u) => (
              <TableRow key={u.fileName + u.dateUploaded}>
                <TableCell>{u.fileName}</TableCell>
                <TableCell>{u.rows}</TableCell>
                <TableCell>{u.mbSize}</TableCell>
                <TableCell>{u.dateUploaded}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Paper>
    </Box>
  );
}
