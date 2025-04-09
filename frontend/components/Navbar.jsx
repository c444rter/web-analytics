// components/Navbar.jsx
"use client";

// Import required Material UI and NextAuth components
import React, { useState } from "react";
import { AppBar, Toolbar, Typography, IconButton, Menu, MenuItem, Button } from "@mui/material";
import AccountCircle from "@mui/icons-material/AccountCircle";
import { useSession, signOut } from "next-auth/react";
import { useRouter } from "next/navigation";

export default function Navbar() {
  const router = useRouter();
  const { data: session, status } = useSession();
  const [anchorEl, setAnchorEl] = useState(null);

  // When user clicks, open the account menu.
  const handleMenu = (event) => {
    setAnchorEl(event.currentTarget);
  };

  // Close the menu.
  const handleClose = () => setAnchorEl(null);

  // Sign out and then redirect to home.
  const handleSignOut = async () => {
    setAnchorEl(null);
    await signOut();
    router.push("/");
  };

  // Navigate to the account details page.
  const handleAccountDetails = () => {
    setAnchorEl(null);
    router.push("/account");
  };

  // Navigate to the historical uploads page.
  const handleHistorical = () => {
    setAnchorEl(null);
    router.push("/historical");
  };

  const handleUpload = () => {
    setAnchorEl(null);
    router.push("/upload");
  };

  const handleDashboard = () => {
    setAnchorEl(null);
    router.push("/dashboard");
  };

  return (
    <AppBar position="static" sx={{ marginBottom: 2 }}>
      <Toolbar>
        <Typography variant="h6" sx={{ flexGrow: 1, cursor: "pointer" }} onClick={() => router.push("/")}>
          mydavids.com
        </Typography>
        {status === "authenticated" ? (
          <div>
            <IconButton size="large" color="inherit" onClick={handleMenu}>
              <AccountCircle />
            </IconButton>
            <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={handleClose}>
              <MenuItem onClick={handleAccountDetails}>Account</MenuItem>
              <MenuItem onClick={handleHistorical}>Uploads</MenuItem>
              <MenuItem onClick={handleUpload}>New Data</MenuItem>
              <MenuItem onClick={handleDashboard}>Dashboards</MenuItem>
              <MenuItem onClick={handleSignOut}>Log Out</MenuItem>
            </Menu>
          </div>
        ) : (
          <Button color="inherit" onClick={() => router.push("/login")}>
            Sign In!
          </Button>
        )}
      </Toolbar>
    </AppBar>
  );
}
