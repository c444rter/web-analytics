// components/StyleForecastChart.jsx
import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  FormControl, 
  InputLabel, 
  Select, 
  MenuItem, 
  CircularProgress,
  Button,
  Grid,
  Slider,
  Tooltip,
  Tabs,
  Tab,
  TextField,
  InputAdornment,
  Chip,
  IconButton
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import ClearAllIcon from '@mui/icons-material/ClearAll';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer } from 'recharts';
import { useAvailableModels, useStyleForecast } from '../hooks/useProjections';

const StyleForecastChart = ({ uploadId }) => {
  const [days, setDays] = useState(30);
  const [modelType, setModelType] = useState('naive');
  const [selectedStyles, setSelectedStyles] = useState([]);
  const [tabValue, setTabValue] = useState(0);
  const [forecastSubTabValue, setForecastSubTabValue] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  
  // Fetch available models
  const { 
    data: availableModels, 
    isLoading: loadingModels 
  } = useAvailableModels();
  
  // Fetch style forecast data
  const { 
    data: forecastData, 
    isLoading: loadingForecast, 
    isError: forecastError,
    refreshStyleForecast
  } = useStyleForecast(uploadId, days, modelType, !!uploadId);
  
  // Handle days slider change
  const handleDaysChange = (event, newValue) => {
    setDays(newValue);
  };
  
  // Handle model type change
  const handleModelChange = (event) => {
    setModelType(event.target.value);
  };
  
  // This function is no longer needed as we're using the inline onChange handler
  // with setSelectedStyles directly in the Select component
  
  // Handle main tab change
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };
  
  // Handle forecast sub-tab change (Revenue vs Quantity)
  const handleForecastSubTabChange = (event, newValue) => {
    setForecastSubTabValue(newValue);
  };
  
  // Handle search term change
  const handleSearchChange = (event) => {
    setSearchTerm(event.target.value);
  };
  
  // Handle clear all styles
  const handleClearAllStyles = () => {
    setSelectedStyles([]);
  };
  
  // Set the first style as selected when data loads
  useEffect(() => {
    if (forecastData?.forecast?.styles?.length > 0 && selectedStyles.length === 0) {
      setSelectedStyles([forecastData.forecast.styles[0]]);
    }
  }, [forecastData, selectedStyles]);
  
  // Format data for the chart
  const formatChartData = () => {
    if (!forecastData || !forecastData.forecast || !forecastData.forecast.forecast || selectedStyles.length === 0) {
      return [];
    }
    
    // Group forecast data by date
    const dateMap = new Map();
    
    forecastData.forecast.forecast.forEach(item => {
      if (selectedStyles.includes(item.style)) {
        const date = item.date;
        if (!dateMap.has(date)) {
          dateMap.set(date, { date });
        }
        
        // Add style-specific data with style name as key
        const entry = dateMap.get(date);
        entry[`revenue_${item.style}`] = parseFloat(item.predicted_revenue).toFixed(2);
        entry[`quantity_${item.style}`] = item.predicted_quantity;
      }
    });
    
    return Array.from(dateMap.values());
  };
  
  const chartData = formatChartData();
  
  // Get style metrics for selected styles
  const getStyleMetrics = () => {
    if (!forecastData || !forecastData.forecast || !forecastData.forecast.style_metrics || selectedStyles.length === 0) {
      return [];
    }
    
    return forecastData.forecast.style_metrics.filter(metric => 
      selectedStyles.includes(metric.style)
    );
  };
  
  const styleMetrics = getStyleMetrics();
  
  return (
    <Paper sx={{ p: 3, mb: 3 }}>
      <Typography variant="h6" gutterBottom>
        Style-Based Sales Forecast
      </Typography>
      
      <Tabs 
        value={tabValue} 
        onChange={handleTabChange}
        sx={{ mb: 3 }}
      >
        <Tab label="Forecast" />
        <Tab label="Style Metrics" />
      </Tabs>
      
      {tabValue === 0 && (
        <>
          <Grid container spacing={3} sx={{ mb: 3 }}>
            <Grid item xs={12} md={4}>
              <Box sx={{ width: '100%' }}>
                <Typography id="days-slider" gutterBottom>
                  Forecast Period (Days)
                </Typography>
                <Slider
                  value={days}
                  onChange={handleDaysChange}
                  aria-labelledby="days-slider"
                  valueLabelDisplay="auto"
                  step={10}
                  marks
                  min={10}
                  max={90}
                />
              </Box>
            </Grid>
            
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel id="model-select-label">Forecast Model</InputLabel>
                <Select
                  labelId="model-select-label"
                  id="model-select"
                  value={modelType}
                  label="Forecast Model"
                  onChange={handleModelChange}
                  disabled={loadingModels}
                >
                  {loadingModels ? (
                    <MenuItem value="">
                      <em>Loading models...</em>
                    </MenuItem>
                  ) : (
                    availableModels?.map(model => (
                      <MenuItem key={model.id} value={model.id}>
                        {/* Only use Tooltip when not disabled */}
                        {!loadingModels ? (
                          <Tooltip title={model.description} placement="right">
                            <span>{model.name}</span>
                          </Tooltip>
                        ) : (
                          <span>{model.name}</span>
                        )}
                      </MenuItem>
                    ))
                  )}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel id="style-select-label">Product Styles</InputLabel>
                <Select
                  labelId="style-select-label"
                  id="style-select"
                  multiple
                  value={selectedStyles}
                  label="Product Styles"
                  onChange={(event) => setSelectedStyles(event.target.value)}
                  disabled={loadingForecast || !forecastData}
                  renderValue={(selected) => (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {selected.map((value) => (
                        <Chip key={value} label={value} size="small" />
                      ))}
                    </Box>
                  )}
                  MenuProps={{
                    PaperProps: {
                      style: {
                        maxHeight: 300
                      }
                    }
                  }}
                >
                  <Box sx={{ p: 1, position: 'sticky', top: 0, bgcolor: 'background.paper', zIndex: 1 }}>
                    <TextField
                      size="small"
                      placeholder="Search styles..."
                      value={searchTerm}
                      onChange={handleSearchChange}
                      fullWidth
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <SearchIcon fontSize="small" />
                          </InputAdornment>
                        ),
                        endAdornment: searchTerm && (
                          <InputAdornment position="end">
                            <IconButton 
                              size="small" 
                              onClick={() => setSearchTerm('')}
                              edge="end"
                            >
                              <ClearAllIcon fontSize="small" />
                            </IconButton>
                          </InputAdornment>
                        )
                      }}
                    />
                    <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 1 }}>
                      <Button 
                        size="small" 
                        onClick={handleClearAllStyles}
                        startIcon={<ClearAllIcon />}
                        disabled={selectedStyles.length === 0}
                      >
                        Clear All
                      </Button>
                    </Box>
                  </Box>
                  
                  {loadingForecast ? (
                    <MenuItem value="">
                      <em>Loading styles...</em>
                    </MenuItem>
                  ) : forecastData?.forecast?.styles ? (
                    forecastData.forecast.styles
                      .filter(style => style.toLowerCase().includes(searchTerm.toLowerCase()))
                      .map(style => (
                        <MenuItem key={style} value={style}>
                          {style}
                        </MenuItem>
                      ))
                  ) : (
                    <MenuItem value="">
                      <em>No styles available</em>
                    </MenuItem>
                  )}
                </Select>
              </FormControl>
            </Grid>
          </Grid>
          
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
            {loadingForecast ? (
              <Button 
                variant="outlined" 
                disabled={true}
              >
                Refresh Forecast
              </Button>
            ) : (
              <Button 
                variant="outlined" 
                onClick={refreshStyleForecast}
              >
                Refresh Forecast
              </Button>
            )}
          </Box>
          
          {loadingForecast ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          ) : forecastError ? (
            <Typography color="error">
              Error loading forecast data. Please try again.
            </Typography>
          ) : chartData.length === 0 ? (
            <Typography>
              No forecast data available for the selected styles. Please select different styles or upload.
            </Typography>
          ) : (
            <Box sx={{ height: 400, width: '100%' }}>
              <Tabs 
                value={forecastSubTabValue} 
                onChange={handleForecastSubTabChange}
                sx={{ mb: 2 }}
              >
                <Tab label="Revenue Forecast" />
                <Tab label="Quantity Forecast" />
              </Tabs>
              
              {forecastSubTabValue === 0 ? (
                // Revenue Chart
                <ResponsiveContainer>
                  <LineChart
                    data={chartData}
                    margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="date" 
                      tick={{ fontSize: 12 }}
                      interval="preserveStartEnd"
                    />
                    <YAxis domain={['auto', 'auto']} />
                    <RechartsTooltip />
                    <Legend />
                    {selectedStyles.map((style, index) => {
                      // Generate a color based on index
                      const colors = ['#8884d8', '#82ca9d', '#ffc658', '#ff8042', '#0088fe', '#00C49F'];
                      const color = colors[index % colors.length];
                      
                      return (
                        <Line
                          key={style}
                          type="monotone"
                          dataKey={`revenue_${style}`}
                          stroke={color}
                          name={`${style} Revenue ($)`}
                          dot={{ r: 2 }}
                        />
                      );
                    })}
                  </LineChart>
                </ResponsiveContainer>
              ) : forecastSubTabValue === 1 && (
                // Quantity Chart
                <ResponsiveContainer>
                  <LineChart
                    data={chartData}
                    margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="date" 
                      tick={{ fontSize: 12 }}
                      interval="preserveStartEnd"
                    />
                    <YAxis domain={['auto', 'auto']} />
                    <RechartsTooltip />
                    <Legend />
                    {selectedStyles.map((style, index) => {
                      // Generate a color based on index
                      const colors = ['#8884d8', '#82ca9d', '#ffc658', '#ff8042', '#0088fe', '#00C49F'];
                      const color = colors[index % colors.length];
                      
                      return (
                        <Line
                          key={style}
                          type="monotone"
                          dataKey={`quantity_${style}`}
                          stroke={color}
                          name={`${style} Quantity (Units)`}
                          dot={{ r: 2 }}
                        />
                      );
                    })}
                  </LineChart>
                </ResponsiveContainer>
              )}
            </Box>
          )}
        </>
      )}
      
      {tabValue === 1 && (
        <Box sx={{ p: 2 }}>
          <Typography variant="subtitle1" gutterBottom>
            Selected Styles: {selectedStyles.length > 0 ? selectedStyles.join(', ') : 'None selected'}
          </Typography>
          
          {styleMetrics.length > 0 ? (
            <Grid container spacing={2}>
              {styleMetrics.map(metric => (
                <Grid item xs={12} md={6} key={metric.style} sx={{ display: 'flex' }}>
                  <Paper elevation={2} sx={{ p: 2, width: '100%' }}>
                    <Typography variant="subtitle2" gutterBottom>
                      {metric.style}
                    </Typography>
                    <Grid container spacing={2}>
                      <Grid item xs={12} md={4}>
                        <Typography variant="body2">
                          Mean Quantity: {metric.mean_quantity.toFixed(2)} units
                        </Typography>
                      </Grid>
                      <Grid item xs={12} md={4}>
                        <Typography variant="body2">
                          Mean Revenue: ${metric.mean_revenue.toFixed(2)}
                        </Typography>
                      </Grid>
                      <Grid item xs={12} md={4}>
                        <Typography variant="body2">
                          Days Analyzed: {metric.total_days_analyzed}
                        </Typography>
                      </Grid>
                    </Grid>
                  </Paper>
                </Grid>
              ))}
            </Grid>
          ) : (
            <Typography>
              No metrics available for the selected styles.
            </Typography>
          )}
          
          {forecastData?.forecast?.overall_metrics && (
            <Box sx={{ mt: 4 }}>
              <Typography variant="subtitle1" gutterBottom>
                Overall Metrics (All Styles)
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} md={4}>
                  <Typography variant="body2">
                    Mean Quantity: {forecastData.forecast.overall_metrics.mean_quantity.toFixed(2)} units
                  </Typography>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Typography variant="body2">
                    Mean Revenue: ${forecastData.forecast.overall_metrics.mean_revenue.toFixed(2)}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Typography variant="body2">
                    Days Analyzed: {forecastData.forecast.overall_metrics.total_days_analyzed}
                  </Typography>
                </Grid>
              </Grid>
            </Box>
          )}
        </Box>
      )}
    </Paper>
  );
};

export default StyleForecastChart;
