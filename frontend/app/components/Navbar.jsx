"use client";

import React, { useState } from "react";
import { AppBar, Toolbar, Typography, IconButton, Menu, MenuItem, Button } from "@mui/material";
import AccountCircle from "@mui/icons-material/AccountCircle";
import { useSession, signOut } from "next-auth/react";
import { useRouter } from "next/navigation";

export default function Navbar() {
  const router = useRouter();
  const { data: session, status } = useSession();
  const [anchorEl, setAnchorEl] = useState(null);

  const handleMenu = (event) => {
    setAnchorEl(event.currentTarget);
  };
  const handleClose = () => setAnchorEl(null);

  const handleSignOut = async () => {
    setAnchorEl(null);
    await signOut();
    router.push("/"); // or redirect anywhere
  };

  const handleAccountDetails = () => {
    setAnchorEl(null);
    router.push("/account");
  };

  const handleHistorical = () => {
    setAnchorEl(null);
    router.push("/historical");
  };

  return (
    <AppBar position="static" sx={{ marginBottom: 2 }}>
      <Toolbar>
        <Typography variant="h6" sx={{ flexGrow: 1, cursor: "pointer" }} onClick={() => router.push("/")}>
          MyAnalytics
        </Typography>
        
        {status === "authenticated" ? (
          <div>
            <IconButton size="large" color="inherit" onClick={handleMenu}>
              <AccountCircle />
            </IconButton>
            <Menu
              anchorEl={anchorEl}
              open={Boolean(anchorEl)}
              onClose={handleClose}
            >
              <MenuItem onClick={handleAccountDetails}>Account Details</MenuItem>
              <MenuItem onClick={handleHistorical}>Historical Uploads</MenuItem>
              <MenuItem onClick={handleSignOut}>Sign Out</MenuItem>
            </Menu>
          </div>
        ) : (
          <Button color="inherit" onClick={() => router.push("/login")}>
            Sign In
          </Button>
        )}
      </Toolbar>
    </AppBar>
  );
}
