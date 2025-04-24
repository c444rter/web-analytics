"use client";

import React, { useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import {
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Box,
  Stack
} from "@mui/material";

export default function AccountPage() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [newPassword, setNewPassword] = useState("");

  // Redirect unauthenticated users to the login page.
  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/login");
    }
  }, [status, router]);

  // Placeholder function to handle password updates.
  const handlePasswordChange = async () => {
    alert("Password change not yet implemented!");
  };

  if (status === "loading") {
    return (
      <Container maxWidth="sm" sx={{ mt: 4 }}>
        <Paper elevation={3} sx={{ p: 3 }}>
          <Typography>Loading...</Typography>
        </Paper>
      </Container>
    );
  }
  if (status === "unauthenticated") {
    return null;
  }

  return (
    <Container maxWidth="sm" sx={{ mt: 4 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h4" textAlign="center" mb={3}>
          Account Details
        </Typography>
        <Stack spacing={2}>
          <Typography variant="body1">
            Email: {session?.user?.email}
          </Typography>
          <Typography variant="body1">
            Name: {session?.user?.name || "No name provided"}
          </Typography>
        </Stack>

        <Box mt={4}>
          <Typography variant="h6" mb={2}>
            Change Password
          </Typography>
          <Stack spacing={2}>
            <TextField
              label="New Password"
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
            />
            <Button variant="contained" onClick={handlePasswordChange}>
              Update Password
            </Button>
          </Stack>
        </Box>
      </Paper>
    </Container>
  );
}
