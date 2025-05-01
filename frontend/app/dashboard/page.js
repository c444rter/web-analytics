"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { useSelector, useDispatch } from "react-redux";
import { setDashboardSelection } from "../../store/store";
import {
  Box,
  Typography,
  Button,
  Checkbox,
  FormControlLabel,
  CircularProgress,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Dialog,
  DialogTitle,
  DialogContent,
  ToggleButtonGroup,
  ToggleButton,
  Paper,
  Divider,
  Container,
  Grid,
  Chip,
  Card,
  CardContent,
  IconButton,
  Tooltip,
  useTheme,
  Alert
} from "@mui/material";
import FilterListIcon from "@mui/icons-material/FilterList";
import RefreshIcon from "@mui/icons-material/Refresh";
import InfoIcon from "@mui/icons-material/Info";
import SettingsIcon from "@mui/icons-material/Settings";
import DashboardIcon from "@mui/icons-material/Dashboard";

// Aggregator block that references KPICard, KPILineChart, etc.
import AggregatorBlock from "../../components/AggregatorBlock";

// Import your TanStack Query hooks for analytics
import useAnalyticsFull from "../../hooks/useAnalyticsFull";
import useAnalyticsAvailable from "../../hooks/useAnalyticsAvailable";
import useAnalyticsCustom from "../../hooks/useAnalyticsCustom";

// Import your hook to fetch historical uploads
import useHistoricalUploads from "../../hooks/useHistoricalUploads";

// Component to handle search params
function DashboardContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const theme = useTheme();

  const dispatch = useDispatch();
  const cachedSelection = useSelector((state) => state.app.dashboardSelection);
  
  // Use query params or cached selection to initialize uploadId and mode
  const queryUploadId = searchParams.get("upload_id");
  const queryMode = searchParams.get("mode");
  
  // Initialize from query params first, then fall back to cached selection
  const initialUploadId = queryUploadId || (cachedSelection?.uploadId || "");
  const initialMode = queryMode || (cachedSelection?.mode || "default");

  // State for current upload selection (for historical switching)
  const [uploadId, setUploadId] = useState(initialUploadId);
  const [mode, setMode] = useState(initialMode);
  
  // Sync state with URL parameters when they change
  useEffect(() => {
    const newUploadId = searchParams.get("upload_id");
    const newMode = searchParams.get("mode");
    
    if (newUploadId && newUploadId !== uploadId) {
      setUploadId(newUploadId);
    }
    
    if (newMode && newMode !== mode) {
      setMode(newMode);
    }
  }, [searchParams, uploadId, mode]);
  
  // No longer needed since we removed dashboard controls
  // const [showKpiSelector, setShowKpiSelector] = useState(false);
  // const [selectedDefaultKpis, setSelectedDefaultKpis] = useState([]);
  // const [filterKpis, setFilterKpis] = useState(false);

  // For "historical uploads" switching—fetch past uploads.
  const {
    data: historicalUploads,
    isLoading: loadingHistory,
    isError: errorHistory,
    refetch: refetchUploads
  } = useHistoricalUploads();

  // Refresh uploads list when the component mounts or when uploadId changes
  useEffect(() => {
    // Always refresh the uploads list when the component mounts with an uploadId
    if (uploadId) {
      console.log("Refreshing uploads list for upload ID:", uploadId);
      refetchUploads();
    }
  }, [uploadId, refetchUploads]);
  
  // Update the cached selection with the file name when the historical uploads data is loaded
  useEffect(() => {
    if (uploadId && historicalUploads && !loadingHistory) {
      const selectedUpload = historicalUploads.find(upload => upload.id === uploadId);
      if (selectedUpload && selectedUpload.file_name) {
        // Update the cached selection with the file name
        dispatch(setDashboardSelection({
          uploadId: uploadId,
          mode: mode,
          fileName: selectedUpload.file_name
        }));
      }
    }
  }, [uploadId, historicalUploads, loadingHistory, mode, dispatch]);

  // For "custom" mode, fetch available aggregator keys
  const {
    data: availableMetrics,
    isLoading: loadingAvailable,
    isError: errorAvailable,
  } = useAnalyticsAvailable(mode === "custom");

  // For "default" mode, fetch all analytics based on the current uploadId
  const {
    data: fullAnalytics,
    isLoading: loadingFull,
    isError: errorFull,
    refetch: refetchAnalytics
  } = useAnalyticsFull(uploadId, mode === "default");

  // For "custom" mode, user picks aggregator keys, then calls the custom endpoint
  const [selectedKeys, setSelectedKeys] = useState([]);
  const {
    mutateAsync: fetchCustomAnalytics,
    data: customAnalytics,
    isLoading: loadingCustom,
    isError: errorCustom,
  } = useAnalyticsCustom();

  useEffect(() => {
    if (!uploadId) {
      console.warn("No upload_id found in query params. Please specify ?upload_id=XYZ");
    }
  }, [uploadId]);

  const handleToggleKey = (key) => {
    setSelectedKeys((prev) =>
      prev.includes(key) ? prev.filter((k) => k !== key) : [...prev, key]
    );
  };
  
  // These functions are no longer needed since we removed dashboard controls

  const handleFetchCustom = async () => {
    if (!uploadId || selectedKeys.length === 0) return;
    await fetchCustomAnalytics({ uploadId, selectedMetrics: selectedKeys });
  };

  // When user selects a different historical upload, update state, route, and cache
  const handleHistoricalChange = (event) => {
    const newUploadId = event.target.value;
    setUploadId(newUploadId);
    
    // Get the file name of the selected upload
    let fileName = null;
    if (historicalUploads) {
      const selectedUpload = historicalUploads.find(upload => upload.id === newUploadId);
      if (selectedUpload) {
        fileName = selectedUpload.file_name;
      }
    }
    
    // Cache the selection in Redux
    dispatch(setDashboardSelection({
      uploadId: newUploadId,
      mode: mode,
      fileName: fileName
    }));
    
    router.push(`/dashboard?upload_id=${newUploadId}&mode=${mode}`);
  };

  // Format KPI key for display
  const formatKpiName = (key) => {
    return key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
  };

  // Group KPIs by category
  const groupKpisByCategory = () => {
    if (!fullAnalytics) return {};
    
    const categories = {
      'Orders': ['orders_summary', 'time_series', 'orders_by_hour', 'orders_by_day_of_week'],
      'Customers': ['repeat_customers'],
      'Geography': ['top_cities_by_orders', 'top_cities_by_revenue'],
      'Products': ['top_products_by_quantity', 'top_products_by_revenue'],
      'Discounts': ['top_discount_codes', 'top_discount_codes_by_savings']
    };
    
    const grouped = {};
    Object.entries(categories).forEach(([category, keys]) => {
      grouped[category] = keys.filter(key => fullAnalytics[key]);
    });
    
    // Add any keys not in predefined categories to "Other"
    const allCategoryKeys = Object.values(categories).flat();
    const otherKeys = Object.keys(fullAnalytics).filter(key => !allCategoryKeys.includes(key));
    if (otherKeys.length > 0) {
      grouped['Other'] = otherKeys;
    }
    
    return grouped;
  };

  // Basic error checks
  if (errorHistory) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert severity="error">Error loading historical uploads. Please try again later.</Alert>
      </Container>
    );
  }
  
  // Only show error messages if we have an uploadId but there's an error
  if (uploadId) {
    if (mode === "default" && errorFull) {
      return (
        <Container maxWidth="lg" sx={{ mt: 4 }}>
          <Alert severity="error">Error loading analytics data. Please try again later.</Alert>
        </Container>
      );
    }
    if (mode === "custom" && errorAvailable) {
      return (
        <Container maxWidth="lg" sx={{ mt: 4 }}>
          <Alert severity="error">Error loading available metrics. Please try again later.</Alert>
        </Container>
      );
    }
    if (mode === "custom" && errorCustom) {
      return (
        <Container maxWidth="lg" sx={{ mt: 4 }}>
          <Alert severity="error">Error calling custom analytics endpoint. Please try again later.</Alert>
        </Container>
      );
    }
  }

  const groupedKpis = groupKpisByCategory();

  return (
    <Container maxWidth="lg" sx={{ mt: 2 }}>
      {/* Page Header */}
      <Box sx={{ mb: 4, display: 'flex', alignItems: 'center' }}>
        <DashboardIcon sx={{ fontSize: 32, mr: 2, color: theme.palette.secondary.main }} />
        <Typography variant="h4" component="h1">
          Dashboard
        </Typography>
        
        {uploadId && mode === "default" && !loadingFull && (
          <span>
            <Tooltip title="Refresh analytics data">
              <IconButton 
                onClick={() => refetchAnalytics()} 
                sx={{ ml: 2 }}
                color="primary"
              >
                <RefreshIcon />
              </IconButton>
            </Tooltip>
          </span>
        )}
      </Box>
      

      {/* Historical Upload Selector */}
      <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Data Source
          </Typography>
          {loadingHistory ? (
            <IconButton 
              size="small"
              disabled={true}
            >
              <RefreshIcon fontSize="small" />
            </IconButton>
          ) : (
            <Tooltip title="Refresh uploads list">
              <IconButton 
                onClick={() => refetchUploads()} 
                size="small"
              >
                <RefreshIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          )}
        </Box>
        
        <FormControl fullWidth>
          <InputLabel id="upload-select-label">Select Upload</InputLabel>
          <Select
            labelId="upload-select-label"
            value={uploadId}
            label="Select Upload"
            onChange={handleHistoricalChange}
            disabled={loadingHistory}
            // No custom renderValue needed - the dropdown will display the selected item's text content
          >
            {loadingHistory && (
              <MenuItem value="">
                <em>Loading uploads...</em>
              </MenuItem>
            )}
            {historicalUploads && historicalUploads.length > 0 ? (
              historicalUploads.map((upload) => (
                <MenuItem key={upload.id} value={upload.id}>
                  {upload.file_name}
                </MenuItem>
              ))
            ) : (
              <MenuItem value="">
                <em>No uploads available. Please upload data first.</em>
              </MenuItem>
            )}
          </Select>
        </FormControl>
        
        {uploadId && (
          <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
            <ToggleButtonGroup
              value={mode}
              exclusive
              onChange={(e, newMode) => {
                if (newMode) {
                  // Cache the selection in Redux
                  dispatch(setDashboardSelection({
                    uploadId: uploadId,
                    mode: newMode,
                    fileName: cachedSelection?.fileName // Preserve the file name
                  }));
                  
                  router.push(`/dashboard?upload_id=${uploadId}&mode=${newMode}`);
                }
              }}
              size="small"
              aria-label="dashboard mode"
            >
              <ToggleButton value="default">
                Default View
              </ToggleButton>
              <ToggleButton value="custom">
                Custom View
              </ToggleButton>
            </ToggleButtonGroup>
          </Box>
        )}
      </Paper>

      {/* If no uploadId, show upload selection dialog */}
      <Dialog 
        open={!uploadId} 
        onClose={() => {}} // Empty function as we don't want to close without selection
        aria-labelledby="upload-selection-dialog-title"
      >
        <DialogTitle id="upload-selection-dialog-title">Select an Upload</DialogTitle>
        <DialogContent>
          <Typography variant="body1" sx={{ mb: 2 }}>
            Please select an upload to view the dashboard data:
          </Typography>
          <FormControl fullWidth>
            <Select
              value=""
              onChange={handleHistoricalChange}
              displayEmpty
            >
              {loadingHistory && (
                <MenuItem value="">
                  <em>Loading uploads...</em>
                </MenuItem>
              )}
              {historicalUploads && historicalUploads.length > 0 ? (
                historicalUploads.map((upload) => (
                  <MenuItem key={upload.id} value={upload.id}>
                    {upload.file_name}
                  </MenuItem>
                ))
              ) : (
                <MenuItem value="">
                  <em>No uploads available. Please upload data first.</em>
                </MenuItem>
              )}
            </Select>
          </FormControl>
        </DialogContent>
      </Dialog>

      {/* =========================
          DEFAULT MODE: full analytics with KPI selection
         ========================= */}
      {mode === "default" && (
        <>
          {loadingFull ? (
            <Box sx={{ display: "flex", alignItems: "center", justifyContent: "center", py: 8 }}>
              <CircularProgress size={40} sx={{ mr: 2 }} />
              <Typography variant="h6">Loading analytics data...</Typography>
            </Box>
          ) : fullAnalytics?.connection_error ? (
            <Box sx={{ py: 4 }}>
              <Alert severity="warning" sx={{ mb: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <Box>
                    <Typography variant="subtitle1" fontWeight="bold">
                      Backend Connection Error
                    </Typography>
                    <Typography variant="body2">
                      Unable to connect to the analytics server. This could be because:
                    </Typography>
                    <ul>
                      <li>The backend server is not running</li>
                      <li>There's a network issue preventing the connection</li>
                      <li>The server is temporarily unavailable</li>
                    </ul>
                    <Typography variant="body2" mt={1}>
                      Showing fallback data for now. Please check the server status or try again.
                    </Typography>
                  </Box>
                  <Button 
                    variant="outlined" 
                    size="small" 
                    startIcon={<RefreshIcon />}
                    onClick={() => refetchAnalytics()}
                    sx={{ mt: 1, ml: 2 }}
                  >
                    Retry
                  </Button>
                </Box>
              </Alert>
              
              {/* Still show fallback data so the UI is usable */}
              <Box sx={{ mt: 4 }}>
                {Object.entries(groupedKpis).map(([category, keys]) => {
                  return (
                    <Box key={category} sx={{ mb: 5 }}>
                      <Typography 
                        variant="h5" 
                        sx={{ 
                          mb: 2, 
                          pb: 1, 
                          borderBottom: `2px solid ${theme.palette.secondary.main}`,
                          display: 'inline-block'
                        }}
                      >
                        {category} (Fallback Data)
                      </Typography>
                      
                      <Grid container spacing={3}>
                        {keys.map(key => (
                          <Grid item xs={12} md={key === 'orders_summary' || key === 'repeat_customers' ? 12 : 6} lg={key === 'orders_summary' || key === 'repeat_customers' ? 12 : 6} key={key}>
                            <Paper 
                              elevation={2} 
                              sx={{ 
                                p: 2, 
                                height: '100%',
                                transition: 'box-shadow 0.3s ease',
                                '&:hover': {
                                  boxShadow: '0 8px 16px rgba(0, 0, 0, 0.2)',
                                },
                                opacity: 0.7 // Indicate it's fallback data
                              }}
                            >
                              <AggregatorBlock
                                aggregatorKey={key}
                                aggregatorData={fullAnalytics[key]}
                              />
                            </Paper>
                          </Grid>
                        ))}
                      </Grid>
                    </Box>
                  );
                })}
              </Box>
            </Box>
          ) : fullAnalytics && (
            <Box sx={{ mt: 4 }}>
              {Object.entries(groupedKpis).map(([category, keys]) => {
                return (
                  <Box key={category} sx={{ mb: 5 }}>
                    <Typography 
                      variant="h5" 
                      sx={{ 
                        mb: 2, 
                        pb: 1, 
                        borderBottom: `2px solid ${theme.palette.secondary.main}`,
                        display: 'inline-block'
                      }}
                    >
                      {category}
                    </Typography>
                    
                    <Grid container spacing={3}>
                      {keys.map(key => (
                        <Grid item xs={12} md={key === 'orders_summary' || key === 'repeat_customers' ? 12 : 6} lg={key === 'orders_summary' || key === 'repeat_customers' ? 12 : 6} key={key}>
                          <Paper 
                            elevation={2} 
                            sx={{ 
                              p: 2, 
                              height: '100%',
                              transition: 'box-shadow 0.3s ease',
                              '&:hover': {
                                boxShadow: '0 8px 16px rgba(0, 0, 0, 0.2)',
                              }
                            }}
                          >
                            <AggregatorBlock
                              aggregatorKey={key}
                              aggregatorData={fullAnalytics[key]}
                            />
                          </Paper>
                        </Grid>
                      ))}
                    </Grid>
                  </Box>
                );
              })}
            </Box>
          )}
        </>
      )}

      {/* =========================
          CUSTOM MODE: select KPIs to fetch
         ========================= */}
      {mode === "custom" && (
        <Paper sx={{ p: 3, mb: 4 }}>
          <Typography variant="h6" gutterBottom>
            Custom KPI Selection
          </Typography>
          
          <Typography variant="body2" color="textSecondary" paragraph>
            Select which KPI(s) you want to view, then click "Load Selected KPIs."
          </Typography>

          {loadingAvailable ? (
            <Box sx={{ display: "flex", alignItems: "center", gap: 2, my: 3 }}>
              <CircularProgress size={24} />
              <Typography>Loading available metrics...</Typography>
            </Box>
          ) : (
            <Grid container spacing={2} sx={{ my: 2 }}>
              {availableMetrics?.map((metric) => (
                <Grid item xs={12} sm={6} md={4} key={metric.key}>
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={selectedKeys.includes(metric.key)}
                        onChange={() => handleToggleKey(metric.key)}
                        color="secondary"
                      />
                    }
                    label={
                      <Box>
                        <Typography variant="body2" fontWeight="medium">
                          {metric.label}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          {metric.description}
                        </Typography>
                      </Box>
                    }
                    sx={{ 
                      display: 'flex',
                      p: 1,
                      border: '1px solid',
                      borderColor: selectedKeys.includes(metric.key) ? theme.palette.secondary.main : 'transparent',
                      borderRadius: 1,
                      backgroundColor: selectedKeys.includes(metric.key) ? 'rgba(255, 215, 0, 0.05)' : 'transparent',
                      '&:hover': {
                        backgroundColor: 'rgba(255, 255, 255, 0.05)',
                      }
                    }}
                  />
                </Grid>
              ))}
            </Grid>
          )}

          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
            <Button
              variant="contained"
              onClick={handleFetchCustom}
              disabled={!uploadId || selectedKeys.length === 0 || loadingCustom}
              sx={{ 
                px: 4,
                backgroundColor: theme.palette.secondary.main,
                color: '#000',
                '&:hover': {
                  backgroundColor: '#e6c200',
                }
              }}
              startIcon={loadingCustom ? <CircularProgress size={20} color="inherit" /> : null}
            >
              {loadingCustom ? "Loading..." : "Load Selected KPIs"}
            </Button>
          </Box>

          {customAnalytics?.connection_error ? (
            <Box sx={{ mt: 4 }}>
              <Divider sx={{ mb: 3 }} />
              <Alert severity="warning" sx={{ mb: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <Box>
                    <Typography variant="subtitle1" fontWeight="bold">
                      Backend Connection Error
                    </Typography>
                    <Typography variant="body2">
                      Unable to connect to the analytics server. This could be because:
                    </Typography>
                    <ul>
                      <li>The backend server is not running</li>
                      <li>There's a network issue preventing the connection</li>
                      <li>The server is temporarily unavailable</li>
                    </ul>
                    <Typography variant="body2" mt={1}>
                      Showing fallback data for now. Please check the server status or try again.
                    </Typography>
                  </Box>
                  <Button 
                    variant="outlined" 
                    size="small" 
                    startIcon={<RefreshIcon />}
                    onClick={() => handleFetchCustom()}
                    sx={{ mt: 1, ml: 2 }}
                  >
                    Retry
                  </Button>
                </Box>
              </Alert>
              
              <Typography variant="h6" gutterBottom>
                Custom KPI Results (Fallback Data)
              </Typography>
              
              <Grid container spacing={3}>
                {Object.entries(customAnalytics).filter(([key]) => key !== 'connection_error' && key !== 'is_fallback').map(([key, data]) => (
                  <Grid item xs={12} md={key === 'orders_summary' || key === 'repeat_customers' ? 12 : 6} lg={key === 'orders_summary' || key === 'repeat_customers' ? 12 : 6} key={key}>
                    <Paper 
                      elevation={2} 
                      sx={{ 
                        p: 2, 
                        height: '100%',
                        transition: 'box-shadow 0.3s ease',
                        '&:hover': {
                          boxShadow: '0 8px 16px rgba(0, 0, 0, 0.2)',
                        },
                        opacity: 0.7 // Indicate it's fallback data
                      }}
                    >
                      <AggregatorBlock
                        aggregatorKey={key}
                        aggregatorData={data}
                      />
                    </Paper>
                  </Grid>
                ))}
              </Grid>
            </Box>
          ) : customAnalytics && (
            <Box sx={{ mt: 4 }}>
              <Divider sx={{ mb: 3 }} />
              <Typography variant="h6" gutterBottom>
                Custom KPI Results
              </Typography>
              
              <Grid container spacing={3}>
                {Object.entries(customAnalytics).map(([key, data]) => (
                  <Grid item xs={12} md={key === 'orders_summary' || key === 'repeat_customers' ? 12 : 6} lg={key === 'orders_summary' || key === 'repeat_customers' ? 12 : 6} key={key}>
                    <Paper 
                      elevation={2} 
                      sx={{ 
                        p: 2, 
                        height: '100%',
                        transition: 'box-shadow 0.3s ease',
                        '&:hover': {
                          boxShadow: '0 8px 16px rgba(0, 0, 0, 0.2)',
                        }
                      }}
                    >
                      <AggregatorBlock
                        aggregatorKey={key}
                        aggregatorData={data}
                      />
                    </Paper>
                  </Grid>
                ))}
              </Grid>
            </Box>
          )}
        </Paper>
      )}
    </Container>
  );
}

// Main page component with Suspense boundary
export default function DashboardPage() {
  return (
    <Suspense fallback={
      <Container maxWidth="lg" sx={{ mt: 2, display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <CircularProgress />
      </Container>
    }>
      <DashboardContent />
    </Suspense>
  );
}
