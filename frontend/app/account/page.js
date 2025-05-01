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
  Stack,
  Tabs,
  Tab,
  CircularProgress,
  Divider
} from "@mui/material";
import useUserDetails from "../../hooks/useUserDetails";

// Tab Panel component
function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`account-tabpanel-${index}`}
      aria-labelledby={`account-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

export default function AccountPage() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [newPassword, setNewPassword] = useState("");
  const [tabValue, setTabValue] = useState(0);
  
  // Fetch user details including created_at and updated_at
  const { data: userDetails, isLoading: loadingUserDetails } = useUserDetails();

  // Redirect unauthenticated users to the login page.
  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/login");
    }
  }, [status, router]);

  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  // Placeholder function to handle password updates.
  const handlePasswordChange = async () => {
    alert("Password change not yet implemented!");
  };

  // Format date for display
  const formatDate = (dateString) => {
    if (!dateString) return "Not available";
    return new Date(dateString).toLocaleString();
  };

  if (status === "loading" || loadingUserDetails) {
    return (
      <Container maxWidth="sm" sx={{ mt: 4 }}>
        <Paper elevation={3} sx={{ p: 3, display: 'flex', justifyContent: 'center' }}>
          <CircularProgress />
        </Paper>
      </Container>
    );
  }
  
  if (status === "unauthenticated") {
    return null;
  }

  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Paper elevation={3} sx={{ p: 0 }}>
        <Typography variant="h4" textAlign="center" sx={{ pt: 3, pb: 2 }}>
          Account Details
        </Typography>
        
        {/* Tabs */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs 
            value={tabValue} 
            onChange={handleTabChange} 
            aria-label="account tabs"
            centered
          >
            <Tab label="Profile" id="account-tab-0" aria-controls="account-tabpanel-0" />
            <Tab label="Name" id="account-tab-1" aria-controls="account-tabpanel-1" />
            <Tab label="Security" id="account-tab-2" aria-controls="account-tabpanel-2" />
          </Tabs>
        </Box>
        
        {/* Profile Tab */}
        <TabPanel value={tabValue} index={0}>
          <Stack spacing={2}>
            <Typography variant="body1">
              <strong>Email:</strong> {session?.user?.email}
            </Typography>
            <Typography variant="body1">
              <strong>Username:</strong> {userDetails?.username || session?.user?.name || "No name provided"}
            </Typography>
            
            <Divider sx={{ my: 1 }} />
            
            <Typography variant="body1">
              <strong>Account Created:</strong> {formatDate(userDetails?.created_at)}
            </Typography>
            <Typography variant="body1">
              <strong>Last Updated:</strong> {formatDate(userDetails?.updated_at)}
            </Typography>
          </Stack>
        </TabPanel>
        
        {/* Name Tab */}
        <TabPanel value={tabValue} index={1}>
          <Stack spacing={2}>
            <Typography variant="h6" mb={1}>
              Update Your Name
            </Typography>
            <TextField
              label="Username"
              defaultValue={userDetails?.username || ""}
              fullWidth
            />
            <TextField
              label="Display Name"
              defaultValue={session?.user?.name || ""}
              fullWidth
            />
            <Button variant="contained">
              Update Name
            </Button>
          </Stack>
        </TabPanel>
        
        {/* Security Tab */}
        <TabPanel value={tabValue} index={2}>
          <Typography variant="h6" mb={2}>
            Change Password
          </Typography>
          <Stack spacing={2}>
            <TextField
              label="Current Password"
              type="password"
              fullWidth
            />
            <TextField
              label="New Password"
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              fullWidth
            />
            <TextField
              label="Confirm New Password"
              type="password"
              fullWidth
            />
            <Button variant="contained" onClick={handlePasswordChange}>
              Update Password
            </Button>
          </Stack>
        </TabPanel>
      </Paper>
    </Container>
  );
}
