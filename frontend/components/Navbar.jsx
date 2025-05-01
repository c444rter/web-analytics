// components/NavBar.jsx
"use client";

import React, { useState, useEffect } from "react";
import { 
  AppBar, 
  Toolbar, 
  Typography, 
  Button, 
  Box, 
  IconButton, 
  Menu, 
  MenuItem, 
  Avatar,
  Tooltip,
  useTheme,
  useMediaQuery
} from "@mui/material";
import AccountCircle from "@mui/icons-material/AccountCircle";
import DashboardIcon from "@mui/icons-material/Dashboard";
import UploadFileIcon from "@mui/icons-material/UploadFile";
import HistoryIcon from "@mui/icons-material/History";
import ShowChartIcon from "@mui/icons-material/ShowChart";
import PersonIcon from "@mui/icons-material/Person";
import MenuIcon from "@mui/icons-material/Menu";
import { useSession, signOut } from "next-auth/react";
import { useRouter, usePathname } from "next/navigation";

export default function Navbar() {
  const router = useRouter();
  const pathname = usePathname();
  const { data: session, status } = useSession();
  const [anchorEl, setAnchorEl] = useState(null);
  const [mobileMenuAnchorEl, setMobileMenuAnchorEl] = useState(null);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  // Handle account menu
  const handleMenu = (event) => {
    setAnchorEl(event.currentTarget);
  };

  // Handle mobile menu
  const handleMobileMenuOpen = (event) => {
    setMobileMenuAnchorEl(event.currentTarget);
  };

  // Close menus
  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleMobileMenuClose = () => {
    setMobileMenuAnchorEl(null);
  };

  // Sign out and redirect to home
  const handleSignOut = async () => {
    setAnchorEl(null);
    setMobileMenuAnchorEl(null);
    await signOut();
    router.push("/");
  };

  // Navigation handlers
  const handleNavigation = (path) => {
    setMobileMenuAnchorEl(null);
    router.push(path);
  };

  // Check if the current path matches the given path
  const isActive = (path) => {
    if (path === '/') {
      return pathname === '/';
    }
    return pathname?.startsWith(path);
  };

  // Navigation items
  const navItems = [
    { label: "Dashboard", path: "/dashboard", icon: <DashboardIcon /> },
    { label: "Upload Data", path: "/upload", icon: <UploadFileIcon /> },
    { label: "Historical Data", path: "/historical", icon: <HistoryIcon /> },
    { label: "Forecasting", path: "/projections", icon: <ShowChartIcon /> },
  ];

  return (
    <AppBar 
      position="sticky" 
      sx={{ 
        zIndex: (theme) => theme.zIndex.drawer + 1,
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
      }}
    >
      <Toolbar>
        {/* Logo/Brand */}
        <Typography 
          variant="h6" 
          sx={{ 
            flexGrow: { xs: 1, md: 0 }, 
            cursor: "pointer",
            mr: 4,
            fontWeight: 'bold'
          }} 
          onClick={() => router.push("/")}
        >
          DAVIDS
        </Typography>

        {/* Desktop Navigation */}
        {!isMobile && status === "authenticated" && (
          <Box sx={{ display: 'flex', flexGrow: 1 }}>
            {navItems.map((item) => (
              <Button
                key={item.path}
                startIcon={item.icon}
                color="inherit"
                onClick={() => handleNavigation(item.path)}
                sx={{
                  mx: 1,
                  borderBottom: isActive(item.path) ? `2px solid ${theme.palette.secondary.main}` : 'none',
                  borderRadius: 0,
                  paddingBottom: '6px',
                  '&:hover': {
                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                  }
                }}
              >
                {item.label}
              </Button>
            ))}
          </Box>
        )}

        {/* Mobile Menu Icon */}
        {isMobile && status === "authenticated" && (
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleMobileMenuOpen}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
        )}

        {/* User Account */}
        {status === "authenticated" ? (
          <Box>
            <Tooltip title="Account settings">
              <IconButton 
                size="large" 
                color="inherit" 
                onClick={handleMenu}
                sx={{ 
                  ml: 2,
                  border: '1px solid rgba(255, 255, 255, 0.2)',
                  '&:hover': {
                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                  }
                }}
              >
                <AccountCircle />
              </IconButton>
            </Tooltip>
            <Menu 
              anchorEl={anchorEl} 
              open={Boolean(anchorEl)} 
              onClose={handleClose}
              PaperProps={{
                elevation: 3,
                sx: {
                  mt: 1.5,
                  minWidth: 180,
                  backgroundColor: theme.palette.background.paper,
                }
              }}
            >
              <MenuItem onClick={() => { handleClose(); router.push("/account"); }}>
                <PersonIcon sx={{ mr: 1, fontSize: '1.2rem' }} />
                My Account
              </MenuItem>
              <MenuItem onClick={handleSignOut}>
                Log Out
              </MenuItem>
            </Menu>
          </Box>
        ) : (
          <Button 
            variant="outlined" 
            color="inherit" 
            onClick={() => router.push("/login")}
            sx={{ 
              borderColor: 'rgba(255, 255, 255, 0.5)',
              '&:hover': {
                borderColor: 'rgba(255, 255, 255, 0.8)',
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
              }
            }}
          >
            Sign In
          </Button>
        )}

        {/* Mobile Menu */}
        <Menu
          anchorEl={mobileMenuAnchorEl}
          open={Boolean(mobileMenuAnchorEl)}
          onClose={handleMobileMenuClose}
          PaperProps={{
            elevation: 3,
            sx: {
              mt: 1.5,
              minWidth: 200,
              backgroundColor: theme.palette.background.paper,
            }
          }}
        >
          {navItems.map((item) => (
            <MenuItem 
              key={item.path} 
              onClick={() => handleNavigation(item.path)}
              sx={{
                backgroundColor: isActive(item.path) ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
                '&:hover': {
                  backgroundColor: 'rgba(255, 255, 255, 0.05)',
                }
              }}
            >
              {item.icon && <Box component="span" sx={{ mr: 1 }}>{item.icon}</Box>}
              {item.label}
            </MenuItem>
          ))}
        </Menu>
      </Toolbar>
    </AppBar>
  );
}
