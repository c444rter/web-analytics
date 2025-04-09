// app/account/page.js
"use client";

// Import necessary hooks and Material UI components
import React, { useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { Box, Typography, TextField, Button } from "@mui/material";

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
    return <Typography>Loading...</Typography>;
  }
  if (status === "unauthenticated") {
    return null;
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" mb={2}>
        Account Details
      </Typography>
      <Typography>Email: {session?.user?.email}</Typography>
      <Typography>
        Name: {session?.user?.name || "No name provided"}
      </Typography>

      <Box mt={4}>
        <Typography variant="h6">Change Password</Typography>
        <TextField
          label="New Password"
          type="password"
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
          sx={{ mb: 2 }}
        />
        <Button variant="contained" onClick={handlePasswordChange}>
          Update Password
        </Button>
      </Box>
    </Box>
  );
}
