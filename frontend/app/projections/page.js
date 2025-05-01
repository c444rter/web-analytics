"use client";

import React, { useState, useEffect, Suspense } from 'react';
import { 
  Box, 
  Typography, 
  Container, 
  FormControl, 
  InputLabel, 
  Select, 
  MenuItem, 
  CircularProgress,
  Paper,
  Alert,
  ToggleButtonGroup,
  ToggleButton,
  Grid,
  Card,
  CardContent,
  IconButton,
  Tooltip,
  useTheme,
  Divider
} from '@mui/material';
import { useSearchParams, useRouter } from 'next/navigation';
import { useSelector, useDispatch } from "react-redux";
import { setProjectionsSelection } from "../../store/store";
import ShowChartIcon from '@mui/icons-material/ShowChart';
import RefreshIcon from '@mui/icons-material/Refresh';
import StyleIcon from '@mui/icons-material/Style';
import TimelineIcon from '@mui/icons-material/Timeline';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import ForecastChart from '../../components/ForecastChart';
import StyleForecastChart from '../../components/StyleForecastChart';
import useHistoricalUploads from '../../hooks/useHistoricalUploads';

// Component to handle search params
function ProjectionsContent() {
  const router = useRouter();
  const dispatch = useDispatch();
  const cachedSelection = useSelector((state) => state.app.projectionsSelection);
  
  // Use query params or cached selection to initialize uploadId and forecast type
  const searchParams = useSearchParams();
  const queryUploadId = searchParams.get('upload_id');
  const queryType = searchParams.get('type');
  
  // Initialize from query params first, then fall back to cached selection
  const initialUploadId = queryUploadId || (cachedSelection?.uploadId || '');
  const initialForecastType = queryType || (cachedSelection?.forecastType || 'overall');
  
  const [selectedUploadId, setSelectedUploadId] = useState(initialUploadId);
  const [forecastType, setForecastType] = useState(initialForecastType);
  const theme = useTheme();
  
  // Fetch historical uploads for the dropdown
  const { 
    data: historicalUploads, 
    isLoading: loadingUploads, 
    isError: uploadsError,
    refetch: refetchUploads
  } = useHistoricalUploads();
  
  // Sync state with URL parameters when they change
  useEffect(() => {
    const newUploadId = searchParams.get('upload_id');
    const newType = searchParams.get('type');
    
    if (newUploadId && newUploadId !== selectedUploadId) {
      setSelectedUploadId(newUploadId);
    }
    
    if (newType && ['overall', 'style'].includes(newType) && newType !== forecastType) {
      setForecastType(newType);
    }
  }, [searchParams, selectedUploadId, forecastType]);
  
  // Handle upload selection change
  const handleUploadChange = (event) => {
    const newUploadId = event.target.value;
    setSelectedUploadId(newUploadId);
    
    // Cache the selection in Redux
    dispatch(setProjectionsSelection({
      uploadId: newUploadId,
      forecastType: forecastType
    }));
    
    // Update URL
    router.push(`/projections?upload_id=${newUploadId}&type=${forecastType}`);
  };
  
  // Handle forecast type change
  const handleForecastTypeChange = (event, newType) => {
    if (newType !== null) {
      setForecastType(newType);
      
      // Cache the selection in Redux
      dispatch(setProjectionsSelection({
        uploadId: selectedUploadId,
        forecastType: newType
      }));
      
      // Update URL if we have an upload ID
      if (selectedUploadId) {
        router.push(`/projections?upload_id=${selectedUploadId}&type=${newType}`);
      }
    }
  };

  // Forecast type options with descriptions
  const forecastTypes = [
    {
      id: 'overall',
      name: 'Overall Sales Forecast',
      description: 'Predict total sales and order volume across your entire store',
      icon: <TimelineIcon />
    },
    {
      id: 'style',
      name: 'Style-Based Forecast',
      description: 'Analyze sales trends by product style categories',
      icon: <StyleIcon />
    }
  ];
  
  return (
    <Container maxWidth="lg" sx={{ mt: 2 }}>
      {/* Page Header */}
      <Box sx={{ mb: 4, display: 'flex', alignItems: 'center' }}>
        <ShowChartIcon sx={{ fontSize: 32, mr: 2, color: theme.palette.secondary.main }} />
        <Typography variant="h4" component="h1">
          Sales Forecasting
        </Typography>
      </Box>
      
      {/* Data Source Selection */}
      <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Data Source
          </Typography>
          {loadingUploads ? (
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
        
        {uploadsError ? (
          <Alert severity="error" sx={{ mb: 2 }}>
            Error loading uploads. Please refresh the page and try again.
          </Alert>
        ) : (
          <FormControl fullWidth sx={{ mb: 3 }}>
            <InputLabel id="upload-select-label">Select Upload</InputLabel>
            <Select
              labelId="upload-select-label"
              id="upload-select"
              value={selectedUploadId}
              label="Select Upload"
              onChange={handleUploadChange}
              disabled={loadingUploads}
            >
              {loadingUploads ? (
                <MenuItem value="">
                  <em>Loading uploads...</em>
                </MenuItem>
              ) : historicalUploads?.length > 0 ? (
                historicalUploads.map((upload) => (
                  <MenuItem key={upload.id} value={upload.id}>
                    {upload.file_name} - {new Date(upload.uploaded_at).toLocaleString()}
                  </MenuItem>
                ))
              ) : (
                <MenuItem value="">
                  <em>No uploads available</em>
                </MenuItem>
              )}
            </Select>
          </FormControl>
        )}
        
        <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
          For best results, select an upload with at least 30 days of order data. More historical data will improve forecast accuracy.
        </Typography>
        
        {/* Forecast Type Selection */}
        <Typography variant="subtitle1" gutterBottom>
          Forecast Type
        </Typography>
        
        <Grid container spacing={2} sx={{ mb: 2 }}>
          {forecastTypes.map((type) => (
            <Grid item xs={12} sm={6} key={type.id}>
              <Card 
                variant={forecastType === type.id ? "elevation" : "outlined"}
                elevation={forecastType === type.id ? 3 : 0}
                sx={{ 
                  cursor: 'pointer',
                  borderColor: forecastType === type.id ? theme.palette.secondary.main : undefined,
                  backgroundColor: forecastType === type.id ? 'rgba(255, 215, 0, 0.05)' : undefined,
                  transition: 'all 0.2s ease-in-out',
                  '&:hover': {
                    boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)',
                    transform: 'translateY(-2px)'
                  }
                }}
                onClick={() => handleForecastTypeChange(null, type.id)}
              >
                <CardContent sx={{ display: 'flex', alignItems: 'flex-start' }}>
                  <Box sx={{ 
                    mr: 2, 
                    color: forecastType === type.id ? theme.palette.secondary.main : 'inherit',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    p: 1,
                    borderRadius: '50%',
                    backgroundColor: forecastType === type.id ? 'rgba(255, 215, 0, 0.1)' : 'transparent'
                  }}>
                    {type.icon}
                  </Box>
                  <Box>
                    <Typography variant="h6" component="h3" gutterBottom>
                      {type.name}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      {type.description}
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Paper>
      
      {/* Forecast Chart */}
      {selectedUploadId ? (
        forecastType === 'overall' ? (
          <ForecastChart uploadId={selectedUploadId} />
        ) : (
          <StyleForecastChart uploadId={selectedUploadId} />
        )
      ) : (
        <Paper sx={{ p: 4, textAlign: 'center', mb: 4 }}>
          <Typography variant="body1" color="textSecondary">
            Please select an upload to view projections
          </Typography>
        </Paper>
      )}
      
      {/* About Forecasting */}
      <Paper sx={{ p: 3, mt: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <InfoOutlinedIcon sx={{ mr: 1, color: theme.palette.secondary.main }} />
          <Typography variant="h6">
            About Sales Forecasting
          </Typography>
        </Box>
        
        <Divider sx={{ mb: 3 }} />
        
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle1" gutterBottom fontWeight="medium">
              How Our Forecasts Work
            </Typography>
            <Typography variant="body2" paragraph>
              Our projection models use machine learning algorithms to analyze your historical sales data and identify patterns.
              The system considers factors like day-of-week trends, seasonality, and growth patterns to generate forecasts.
            </Typography>
            <Typography variant="body2" paragraph>
              The more historical data you provide, the more accurate your forecasts will be. For best results, we recommend
              having at least 60-90 days of historical order data.
            </Typography>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle1" gutterBottom fontWeight="medium">
              Available Models
            </Typography>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" fontWeight="medium">
                Naive Seasonal Model
              </Typography>
              <Typography variant="body2" paragraph>
                This model uses historical averages by day of week to generate forecasts.
                It's simple but effective for short-term projections when you have limited historical data.
              </Typography>
            </Box>
            
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" fontWeight="medium">
                ARIMA Model
              </Typography>
              <Typography variant="body2" paragraph>
                Auto-Regressive Integrated Moving Average is a more sophisticated statistical model
                that can capture complex patterns in your data. It's better suited for longer-term forecasts when you have
                sufficient historical data.
              </Typography>
            </Box>
            
            <Box>
              <Typography variant="body2" fontWeight="medium">
                Style-Based Forecasts
              </Typography>
              <Typography variant="body2">
                These forecasts break down predictions by product style, allowing you to
                see which styles are trending and plan inventory accordingly. This is especially useful for fashion and apparel
                businesses.
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Paper>
    </Container>
  );
}

// Main page component with Suspense boundary
export default function ProjectionsPage() {
  return (
    <Suspense fallback={
      <Container maxWidth="lg" sx={{ mt: 2, display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <CircularProgress />
      </Container>
    }>
      <ProjectionsContent />
    </Suspense>
  );
}
