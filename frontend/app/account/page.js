// app/account/page.js
"use client";

import React, { useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { Box, Typography, TextField, Button } from "@mui/material";

export default function AccountPage() {
  const { data: session, status } = useSession();
  const router = useRouter();

  const [newPassword, setNewPassword] = useState("");

  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/login");
    }
  }, [status, router]);

  const handlePasswordChange = async () => {
    alert("Password change not yet implemented!");
    // you'd call your /users/change-password route or similar
  };

  if (status === "loading") {
    return <p>Loading...</p>;
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
      {/* If you have a stored full_name in session or fetch from backend */}
      <Typography>Name: (No name in session, fetch from backend if needed)</Typography>

      <Box mt={4}>
        <Typography variant="h6">Change Password</Typography>
        <TextField
          label="New Password"
          type="password"
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
          sx={{ mb: 2 }}
        />
        <br />
        <Button variant="contained" onClick={handlePasswordChange}>
          Update Password
        </Button>
      </Box>
    </Box>
  );
}
