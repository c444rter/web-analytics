"use client";

import React, { useState } from "react";
import { AppBar, Toolbar, Typography, IconButton, Menu, MenuItem, Button } from "@mui/material";
import AccountCircle from "@mui/icons-material/AccountCircle";
import { useRouter } from "next/navigation";

export default function Navbar() {
  const router = useRouter();

  // For the user profile menu
  const [anchorEl, setAnchorEl] = useState(null);

  const handleMenu = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  // Navigate to pages
  const navigateTo = (path) => {
    router.push(path);
    handleClose();
  };

  return (
    <AppBar position="static" sx={{ marginBottom: 2 }}>
      <Toolbar>
        {/* Left side: brand or site name */}
        <Typography variant="h6" sx={{ flexGrow: 1, cursor: "pointer" }} onClick={() => router.push("/")}>
          My Analytics
        </Typography>

        {/* Dashboard link */}
        <Button color="inherit" onClick={() => router.push("/dashboard")}>
          Dashboard
        </Button>

        {/* Upload link */}
        <Button color="inherit" onClick={() => router.push("/upload")}>
          Upload
        </Button>

        {/* Profile Icon */}
        <div>
          <IconButton
            size="large"
            aria-label="account of current user"
            aria-controls="menu-appbar"
            aria-haspopup="true"
            onClick={handleMenu}
            color="inherit"
            sx={{ marginLeft: 2 }}
          >
            <AccountCircle />
          </IconButton>
          <Menu
            id="menu-appbar"
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleClose}
          >
            <MenuItem onClick={() => navigateTo("/account")}>Account Details</MenuItem>
            <MenuItem onClick={() => navigateTo("/history")}>History</MenuItem>
          </Menu>
        </div>
      </Toolbar>
    </AppBar>
  );
}
