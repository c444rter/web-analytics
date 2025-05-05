"use client";

import React, { useState } from "react";
import {
  Box,
  Typography,
  Button,
  Snackbar,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  LinearProgress,
  Container,
  Paper,
  Stack,
  Grid,
  Card,
  CardContent,
  IconButton,
  Tooltip,
  useTheme,
  Divider
} from "@mui/material";
import { useRouter } from "next/navigation";
import useUpload from "../../hooks/useUpload";
import api from "../../lib/api";
import { useDispatch } from "react-redux";
import { setLastUpload, setDashboardSelection } from "../../store/store";
import UploadFileIcon from "@mui/icons-material/UploadFile";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import DashboardIcon from "@mui/icons-material/Dashboard";
import ShowChartIcon from "@mui/icons-material/ShowChart";
import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";

export default function UploadPage() {
  const dispatch = useDispatch();
  const router = useRouter();
  const theme = useTheme();

  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadId, setUploadId] = useState(null);
  const [jobStatus, setJobStatus] = useState("");
  const [progress, setProgress] = useState(0);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: "",
    severity: "info"
  });
  const [kpiDialogOpen, setKpiDialogOpen] = useState(false);
  // Store the most recent upload ID from the API response
  const [latestUploadIdFromApi, setLatestUploadIdFromApi] = useState(null);

  const { mutateAsync, isLoading } = useUpload();

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
  };

  // Poll job progress using the DB upload_id
  const pollJobStatus = (uploadIdToPoll, interval = 3000) => {
    console.log(`Starting to poll job status for upload ID: ${uploadIdToPoll}`);
    
    // Store the interval ID in a ref so we can clear it later
    const intervalId = setInterval(async () => {
      try {
        console.log(`Polling status for upload ID: ${uploadIdToPoll}`);
        const { data } = await api.get(`/uploads/status/${uploadIdToPoll}`);
        console.log("Status response:", data);
        
        const newStatus = data.status || "unknown";
        const newPercent = data.percent || 0;
        const statusMessage = data.message || `Status: ${newStatus}`;
        
        console.log(`Status update: ${newStatus}, Progress: ${newPercent}%, Message: ${statusMessage}`);
        
        setJobStatus(newStatus);
        setProgress(newPercent);

        // Always keep the snackbar open during processing
        setSnackbar({
          open: true,
          message: statusMessage,
          severity: newStatus === "completed" ? "success" : 
                   newStatus === "failed" ? "error" : "info"
        });

        if (newStatus === "completed") {
          console.log("Processing completed successfully");
          clearInterval(intervalId);
          if (data.upload_id) {
            setUploadId(data.upload_id);
            setLatestUploadIdFromApi(data.upload_id);
            console.log(`Setting latest upload ID from API: ${data.upload_id}`);
          }
          
          // Show the dialog to choose dashboard view
          setKpiDialogOpen(true);
          
          // Auto-redirect to default dashboard after 10 seconds if user doesn't choose
          const redirectTimer = setTimeout(() => {
            console.log("Auto-redirecting to default dashboard");
            setKpiDialogOpen(false);
            // Use the most recent upload ID (either from state or API response)
            const finalUploadId = latestUploadIdFromApi || data.upload_id || uploadId;
            console.log(`Auto-redirecting with upload ID: ${finalUploadId}`);
            if (finalUploadId) {
              // Store the selection in Redux before navigating
              dispatch(setDashboardSelection({
                uploadId: finalUploadId,
                mode: 'default',
                fileName: selectedFile?.name
              }));
              router.push(`/dashboard?upload_id=${finalUploadId}&mode=default`);
            } else {
              router.push("/dashboard");
            }
          }, 10000);
          
          // Store the timer ID so we can clear it if the user makes a selection
          window.redirectTimer = redirectTimer;
        } else if (newStatus === "failed") {
          console.log("Processing failed");
          clearInterval(intervalId);
        }
      } catch (err) {
        console.error("Error polling job status:", err);
        // Don't clear the interval on error, just show an error message
        // and continue polling
        setSnackbar({
          open: true,
          message: "Error checking job status. Will retry...",
          severity: "warning"
        });
      }
    }, interval);
    
    // Return the interval ID so it can be cleared if needed
    return intervalId;
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    
    // Show initial loading state
    setSnackbar({
      open: true,
      message: "Uploading file...",
      severity: "info"
    });
    
    const formData = new FormData();
    formData.append("file", selectedFile);
    formData.append("file_name", selectedFile.name);
    
    try {
      console.log("Starting file upload");
      const data = await mutateAsync(formData);
      console.log("Upload response:", data);
      
      dispatch(
        setLastUpload({
          timestamp: new Date().toISOString(),
          fileName: selectedFile.name
        })
      );
      
      // Show upload success message
      setSnackbar({
        open: true,
        message: data.message || "File uploaded! Processing started...",
        severity: "info"
      });
      
      // Ensure we get a valid DB upload_id from the response
      if (data.upload_id) {
        setUploadId(data.upload_id);
        setLatestUploadIdFromApi(data.upload_id);
        console.log(`Starting polling for upload_id: ${data.upload_id}`);
        // Start polling using the DB upload id (not the Redis job id)
        pollJobStatus(data.upload_id);
      } else {
        console.error("upload_id is missing in response:", data);
        setSnackbar({
          open: true,
          message: "Upload succeeded but tracking ID is missing. Processing status may not be available.",
          severity: "warning"
        });
      }
    } catch (err) {
      console.error("Upload error:", err);
      
      // Get a user-friendly error message
      let errorMessage = "Error uploading file.";
      if (err.isUploadError) {
        // Use the custom error message from our hook
        errorMessage = err.message;
      } else if (err.response?.data?.detail) {
        // Use the error detail from the API
        errorMessage = `Upload error: ${err.response.data.detail}`;
      }
      
      setSnackbar({
        open: true,
        message: errorMessage,
        severity: "error"
      });
    }
  };

  const handleChooseDefault = () => {
    // Clear the auto-redirect timer if it exists
    if (window.redirectTimer) {
      clearTimeout(window.redirectTimer);
      window.redirectTimer = null;
    }
    
    setKpiDialogOpen(false);
    // Use the most recent upload ID (either from state or API response)
    const finalUploadId = latestUploadIdFromApi || uploadId;
    if (finalUploadId) {
      // Store the selection in Redux before navigating
      dispatch(setDashboardSelection({
        uploadId: finalUploadId,
        mode: 'default',
        fileName: selectedFile?.name
      }));
      router.push(`/dashboard?upload_id=${finalUploadId}&mode=default`);
    } else {
      router.push("/dashboard");
    }
  };

  const handleChooseCustom = () => {
    // Clear the auto-redirect timer if it exists
    if (window.redirectTimer) {
      clearTimeout(window.redirectTimer);
      window.redirectTimer = null;
    }
    
    setKpiDialogOpen(false);
    // Use the most recent upload ID (either from state or API response)
    const finalUploadId = latestUploadIdFromApi || uploadId;
    if (finalUploadId) {
      // Store the selection in Redux before navigating
      dispatch(setDashboardSelection({
        uploadId: finalUploadId,
        mode: 'custom',
        fileName: selectedFile?.name
      }));
      router.push(`/dashboard?upload_id=${finalUploadId}&mode=custom`);
    } else {
      router.push("/dashboard");
    }
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 2 }}>
      {/* Page Header */}
      <Box sx={{ mb: 4, display: 'flex', alignItems: 'center' }}>
        <UploadFileIcon sx={{ fontSize: 32, mr: 2, color: theme.palette.secondary.main }} />
        <Typography variant="h4" component="h1">
          Upload Data
        </Typography>
      </Box>
      
      <Grid container spacing={4}>
        <Grid item xs={12} md={7}>
          {/* Upload Section */}
          <Paper elevation={3} sx={{ p: 4, height: '100%' }}>
            <Typography variant="h5" gutterBottom>
              Upload Your Shopify Order Data
            </Typography>
            
            <Typography variant="body2" color="textSecondary" paragraph sx={{ mb: 4 }}>
              Upload your Shopify order export files to analyze sales performance and generate forecasts.
              We support CSV and Excel (XLSX) file formats.
            </Typography>
            
            <Box 
              sx={{ 
                border: '2px dashed',
                borderColor: theme.palette.secondary.main,
                borderRadius: 2,
                p: 4,
                textAlign: 'center',
                backgroundColor: 'rgba(255, 215, 0, 0.05)',
                mb: 4
              }}
            >
              <CloudUploadIcon sx={{ fontSize: 60, color: theme.palette.secondary.main, mb: 2 }} />
              
              <Typography variant="h6" gutterBottom>
                Drag & Drop or Select File
              </Typography>
              
              <Typography variant="body2" color="textSecondary" paragraph>
                Accepted formats: .csv, .xlsx
              </Typography>
              
              <input 
                type="file" 
                accept=".csv,.xlsx" 
                onChange={handleFileChange}
                id="file-upload"
                style={{ display: 'none' }}
              />
              
              <label htmlFor="file-upload">
                <Button
                  variant="outlined"
                  component="span"
                  sx={{ 
                    mt: 2,
                    borderColor: theme.palette.secondary.main,
                    color: theme.palette.secondary.main,
                    '&:hover': {
                      borderColor: '#e6c200',
                      backgroundColor: 'rgba(255, 215, 0, 0.1)',
                    }
                  }}
                >
                  Browse Files
                </Button>
              </label>
              
              {selectedFile && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="body2">
                    Selected: <strong>{selectedFile.name}</strong> ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
                  </Typography>
                </Box>
              )}
            </Box>
            
            <Box sx={{ display: 'flex', justifyContent: 'center' }}>
              <Button
                variant="contained"
                onClick={handleUpload}
                disabled={!selectedFile || isLoading}
                startIcon={isLoading ? <CircularProgress size={20} color="inherit" /> : null}
                sx={{ 
                  px: 4, 
                  py: 1.5,
                  backgroundColor: theme.palette.secondary.main,
                  color: '#000',
                  '&:hover': {
                    backgroundColor: '#e6c200',
                  }
                }}
              >
                {isLoading ? "Uploading..." : "Upload File"}
              </Button>
            </Box>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={5}>
          {/* Information Section */}
          <Paper elevation={3} sx={{ p: 4, height: '100%' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <InfoOutlinedIcon sx={{ mr: 1, color: theme.palette.secondary.main }} />
              <Typography variant="h5">
                How It Works
              </Typography>
            </Box>
            
            <Divider sx={{ mb: 3 }} />
            
            <Stack spacing={3}>
              <Box>
                <Typography variant="subtitle1" fontWeight="medium" gutterBottom>
                  1. Export Your Shopify Orders
                </Typography>
                <Typography variant="body2">
                  From your Shopify admin, go to Orders and export your order data as a CSV file.
                </Typography>
              </Box>
              
              <Box>
                <Typography variant="subtitle1" fontWeight="medium" gutterBottom>
                  2. Upload Your File
                </Typography>
                <Typography variant="body2">
                  Upload the exported file here. Our system will process and analyze your order data.
                </Typography>
              </Box>
              
              <Box>
                <Typography variant="subtitle1" fontWeight="medium" gutterBottom>
                  3. View Analytics
                </Typography>
                <Typography variant="body2">
                  Once processing is complete, you can view comprehensive analytics and KPIs in the Dashboard.
                </Typography>
              </Box>
              
              <Box>
                <Typography variant="subtitle1" fontWeight="medium" gutterBottom>
                  4. Generate Forecasts
                </Typography>
                <Typography variant="body2">
                  Use the Forecasting feature to predict future sales trends based on your historical data.
                </Typography>
              </Box>
            </Stack>
            
            <Box sx={{ mt: 4, pt: 2, borderTop: '1px solid rgba(255, 255, 255, 0.1)' }}>
              <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                Need Help?
              </Typography>
              <Typography variant="body2">
                For detailed instructions on exporting Shopify orders and using this tool, please refer to our documentation.
              </Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Status Snackbar */}
      <Snackbar
        anchorOrigin={{ vertical: "top", horizontal: "center" }}
        open={snackbar.open}
        autoHideDuration={null}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert 
          severity={snackbar.severity} 
          sx={{ 
            width: "100%",
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
            borderRadius: 2,
            backgroundColor: snackbar.severity === 'success' 
              ? theme.palette.success.main 
              : snackbar.severity === 'error'
                ? theme.palette.error.main
                : snackbar.severity === 'warning'
                  ? theme.palette.warning.main
                  : theme.palette.secondary.main,
            color: snackbar.severity === 'warning' ? '#000' : '#fff',
            '& .MuiAlert-icon': {
              color: snackbar.severity === 'warning' ? '#000' : '#fff'
            }
          }} 
          icon={snackbar.severity === 'success' ? <CheckCircleIcon /> : false}
        >
          <Box>
            <Typography variant="body2" sx={{ fontWeight: 'medium' }}>{snackbar.message}</Typography>
            {jobStatus && jobStatus !== "completed" && jobStatus !== "failed" && (
              <Box sx={{ mt: 1 }}>
                <LinearProgress 
                  variant="determinate" 
                  value={progress} 
                  sx={{ 
                    height: 8, 
                    borderRadius: 1,
                    backgroundColor: 'rgba(255, 255, 255, 0.3)',
                    '& .MuiLinearProgress-bar': {
                      backgroundColor: snackbar.severity === 'warning' ? '#000' : '#fff'
                    }
                  }} 
                />
                <Typography variant="caption" display="block" textAlign="right" sx={{ mt: 0.5, fontWeight: 'bold' }}>
                  {progress}%
                </Typography>
              </Box>
            )}
          </Box>
        </Alert>
      </Snackbar>

      {/* Dashboard Mode Selection Dialog */}
      <Dialog 
        open={kpiDialogOpen} 
        onClose={() => setKpiDialogOpen(false)}
        PaperProps={{
          sx: {
            borderRadius: 2,
            maxWidth: 500
          }
        }}
      >
        <DialogTitle sx={{ pb: 1 }}>
          Processing Complete!
        </DialogTitle>
        <DialogContent>
          <Typography variant="body1" paragraph>
            Your file has been successfully processed. How would you like to view your data?
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
                onClick={handleChooseDefault}
              >
                <DashboardIcon sx={{ fontSize: 48, color: theme.palette.secondary.main, mb: 1 }} />
                <Typography variant="h6" gutterBottom>Default Dashboard</Typography>
                <Typography variant="body2" color="text.secondary">
                  View all analytics and KPIs
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
                onClick={handleChooseCustom}
              >
                <ShowChartIcon sx={{ fontSize: 48, color: theme.palette.secondary.main, mb: 1 }} />
                <Typography variant="h6" gutterBottom>Custom Dashboard</Typography>
                <Typography variant="body2" color="text.secondary">
                  Select specific KPIs to view
                </Typography>
              </Card>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setKpiDialogOpen(false)}>Cancel</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}
