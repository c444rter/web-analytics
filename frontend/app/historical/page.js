// app/historical/page.jsx

"use client";

import React, { useEffect, useState } from "react";
import { 
  Box, 
  Typography, 
  CircularProgress, 
  Dialog, 
  DialogTitle, 
  DialogContent, 
  DialogActions, 
  Button,
  Paper,
  Container,
  Grid,
  Card,
  CardContent,
  IconButton,
  Tooltip,
  Chip,
  Divider,
  useTheme,
  Alert
} from "@mui/material";
import { useRouter } from "next/navigation";
import useHistoricalUploads from "../../hooks/useHistoricalUploads";
import { useSession } from "next-auth/react";
import HistoryIcon from '@mui/icons-material/History';
import DashboardIcon from '@mui/icons-material/Dashboard';
import ShowChartIcon from '@mui/icons-material/ShowChart';
import RefreshIcon from '@mui/icons-material/Refresh';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import InsertDriveFileIcon from '@mui/icons-material/InsertDriveFile';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty';

export default function HistoricalPage() {
  const router = useRouter();
  const { data: session, status } = useSession();
  const theme = useTheme();
  const { 
    data: uploads, 
    isLoading, 
    isError,
    refetch: refetchUploads
  } = useHistoricalUploads();
  
  // State for the dialog
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedUpload, setSelectedUpload] = useState(null);

  // If not authenticated, redirect outside render.
  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/login");
    }
  }, [status, router]);

  // Handle upload click
  const handleUploadClick = (upload) => {
    setSelectedUpload(upload);
    setDialogOpen(true);
  };

  // Handle dialog close
  const handleDialogClose = () => {
    setDialogOpen(false);
  };

  // Handle navigation to dashboard
  const handleDashboardClick = () => {
    if (selectedUpload) {
      router.push(`/dashboard?upload_id=${selectedUpload.id}`);
    }
    setDialogOpen(false);
  };

  // Handle navigation to projections
  const handleProjectionsClick = () => {
    if (selectedUpload) {
      router.push(`/projections?upload_id=${selectedUpload.id}`);
    }
    setDialogOpen(false);
  };

  // Format date for display
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Get status icon and color
  const getStatusInfo = (status) => {
    switch(status.toLowerCase()) {
      case 'completed':
        return { 
          icon: <CheckCircleIcon />, 
          color: '#4caf50',
          label: 'Completed'
        };
      case 'processing':
        return { 
          icon: <HourglassEmptyIcon />, 
          color: '#ff9800',
          label: 'Processing'
        };
      case 'failed':
        return { 
          icon: <ErrorIcon />, 
          color: '#f44336',
          label: 'Failed'
        };
      default:
        return { 
          icon: <HourglassEmptyIcon />, 
          color: '#9e9e9e',
          label: status
        };
    }
  };

  if (isLoading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Box sx={{ display: "flex", alignItems: "center", justifyContent: "center", py: 8 }}>
          <CircularProgress size={40} sx={{ mr: 2 }} />
          <Typography variant="h6">Loading historical uploads...</Typography>
        </Box>
      </Container>
    );
  }

  if (isError) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert severity="error">Error loading historical uploads. Please try again later.</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 2 }}>
      {/* Page Header */}
      <Box sx={{ mb: 4, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <HistoryIcon sx={{ fontSize: 32, mr: 2, color: theme.palette.secondary.main }} />
          <Typography variant="h4" component="h1">
            Historical Data
          </Typography>
        </Box>
        
        {isLoading ? (
          <IconButton 
            color="primary"
            disabled={true}
          >
            <RefreshIcon />
          </IconButton>
        ) : (
          <Tooltip title="Refresh uploads list">
            <IconButton 
              onClick={() => refetchUploads()} 
              color="primary"
            >
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        )}
      </Box>

      {uploads && uploads.length > 0 ? (
        <Grid container spacing={3}>
          {uploads.map((upload) => {
            const statusInfo = getStatusInfo(upload.status);
            
            return (
              <Grid item xs={12} md={6} key={upload.id}>
                <Card 
                  sx={{ 
                    cursor: 'pointer',
                    transition: 'all 0.2s ease-in-out',
                    '&:hover': {
                      boxShadow: '0 8px 16px rgba(0, 0, 0, 0.2)',
                      transform: 'translateY(-4px)'
                    }
                  }}
                  onClick={() => handleUploadClick(upload)}
                >
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 2 }}>
                      <InsertDriveFileIcon sx={{ fontSize: 40, mr: 2, color: theme.palette.secondary.main }} />
                      <Box sx={{ flexGrow: 1 }}>
                        <Typography variant="h6" component="h2" gutterBottom>
                          {upload.file_name}
                        </Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                          <CalendarTodayIcon sx={{ fontSize: 16, mr: 1, color: 'text.secondary' }} />
                          <Typography variant="body2" color="text.secondary">
                            {formatDate(upload.uploaded_at)}
                          </Typography>
                        </Box>
                      </Box>
                      <Chip 
                        icon={statusInfo.icon} 
                        label={statusInfo.label}
                        sx={{ 
                          backgroundColor: `${statusInfo.color}20`,
                          color: statusInfo.color,
                          fontWeight: 'medium'
                        }}
                      />
                    </Box>
                    
                    <Divider sx={{ my: 2 }} />
                    
                    <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 1 }}>
                      <Button 
                        startIcon={<DashboardIcon />}
                        size="small"
                        sx={{ mr: 1 }}
                        onClick={(e) => {
                          e.stopPropagation();
                          router.push(`/dashboard?upload_id=${upload.id}`);
                        }}
                        disabled={upload.status.toLowerCase() !== 'completed'}
                      >
                        Dashboard
                      </Button>
                      <Button 
                        startIcon={<ShowChartIcon />}
                        size="small"
                        onClick={(e) => {
                          e.stopPropagation();
                          router.push(`/projections?upload_id=${upload.id}`);
                        }}
                        disabled={upload.status.toLowerCase() !== 'completed'}
                      >
                        Forecasting
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            );
          })}
        </Grid>
      ) : (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" gutterBottom>No uploads found</Typography>
          <Typography variant="body1" paragraph>
            You haven't uploaded any data files yet.
          </Typography>
          <Button 
            variant="contained" 
            onClick={() => router.push('/upload')}
            sx={{ 
              backgroundColor: theme.palette.secondary.main,
              color: '#000',
              '&:hover': {
                backgroundColor: '#e6c200',
              }
            }}
          >
            Upload Data
          </Button>
        </Paper>
      )}

      {/* Dialog for Dashboard/Projections selection */}
      <Dialog 
        open={dialogOpen} 
        onClose={handleDialogClose}
        PaperProps={{
          sx: {
            borderRadius: 2,
            maxWidth: 500
          }
        }}
      >
        <DialogTitle sx={{ pb: 1 }}>
          {selectedUpload ? `Select View for ${selectedUpload.file_name}` : 'Select View'}
        </DialogTitle>
        <DialogContent>
          <Typography variant="body1" paragraph>
            Choose how you would like to view this data:
          </Typography>
          
          <Grid container spacing={2}>
            <Grid item xs={6}>
              <Card 
                variant="outlined" 
                sx={{ 
                  textAlign: 'center', 
                  p: 2,
                  cursor: 'pointer',
                  transition: 'all 0.2s ease-in-out',
                  '&:hover': {
                    boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)',
                    borderColor: theme.palette.secondary.main
                  }
                }}
                onClick={handleDashboardClick}
              >
                <DashboardIcon sx={{ fontSize: 48, color: theme.palette.secondary.main, mb: 1 }} />
                <Typography variant="h6" gutterBottom>Dashboard</Typography>
                <Typography variant="body2" color="text.secondary">
                  View analytics and KPIs
                </Typography>
              </Card>
            </Grid>
            <Grid item xs={6}>
              <Card 
                variant="outlined" 
                sx={{ 
                  textAlign: 'center', 
                  p: 2,
                  cursor: 'pointer',
                  transition: 'all 0.2s ease-in-out',
                  '&:hover': {
                    boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)',
                    borderColor: theme.palette.secondary.main
                  }
                }}
                onClick={handleProjectionsClick}
              >
                <ShowChartIcon sx={{ fontSize: 48, color: theme.palette.secondary.main, mb: 1 }} />
                <Typography variant="h6" gutterBottom>Forecasting</Typography>
                <Typography variant="body2" color="text.secondary">
                  View sales projections
                </Typography>
              </Card>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={handleDialogClose}>Cancel</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}
