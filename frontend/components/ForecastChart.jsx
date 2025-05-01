// components/ForecastChart.jsx
import React, { useState } from 'react';
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
  Tooltip
} from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer } from 'recharts';
import { useAvailableModels, useForecast } from '../hooks/useProjections';

const ForecastChart = ({ uploadId }) => {
  const [days, setDays] = useState(30);
  const [modelType, setModelType] = useState('naive');
  
  // Fetch available models
  const { 
    data: availableModels, 
    isLoading: loadingModels 
  } = useAvailableModels();
  
  // Fetch forecast data
  const { 
    data: forecastData, 
    isLoading: loadingForecast, 
    isError: forecastError,
    refreshForecast
  } = useForecast(uploadId, days, modelType, !!uploadId);
  
  // Handle days slider change
  const handleDaysChange = (event, newValue) => {
    setDays(newValue);
  };
  
  // Handle model type change
  const handleModelChange = (event) => {
    setModelType(event.target.value);
  };
  
  // Format data for the chart
  const formatChartData = () => {
    if (!forecastData || !forecastData.forecast || !forecastData.forecast.forecast) {
      return [];
    }
    
    return forecastData.forecast.forecast.map(item => ({
      date: item.date,
      revenue: parseFloat(item.predicted_revenue).toFixed(2),
      orders: item.predicted_orders
    }));
  };
  
  const chartData = formatChartData();
  
  return (
    <Paper sx={{ p: 3, mb: 3 }}>
      <Typography variant="h6" gutterBottom>
        Sales Forecast
      </Typography>
      
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
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
        
        <Grid item xs={12} md={6}>
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
            onClick={refreshForecast}
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
          No forecast data available. Please select a different upload or model.
        </Typography>
      ) : (
        <Box sx={{ height: 400, width: '100%' }}>
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
              <YAxis yAxisId="left" />
              <YAxis yAxisId="right" orientation="right" />
              <RechartsTooltip />
              <Legend />
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="revenue"
                stroke="#8884d8"
                name="Predicted Revenue"
                dot={{ r: 2 }}
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="orders"
                stroke="#82ca9d"
                name="Predicted Orders"
                dot={{ r: 2 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </Box>
      )}
      
      {forecastData?.forecast?.metrics && (
        <Box sx={{ mt: 3, p: 2, bgcolor: '#f5f5f5', borderRadius: 1 }}>
          <Typography variant="subtitle2" gutterBottom>
            Forecast Metrics
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={4}>
              <Typography variant="body2">
                Mean Revenue: ${forecastData.forecast.metrics.mean_revenue.toFixed(2)}
              </Typography>
            </Grid>
            <Grid item xs={4}>
              <Typography variant="body2">
                Mean Orders: {forecastData.forecast.metrics.mean_orders.toFixed(1)}
              </Typography>
            </Grid>
            <Grid item xs={4}>
              <Typography variant="body2">
                Days Analyzed: {forecastData.forecast.metrics.total_days_analyzed}
              </Typography>
            </Grid>
          </Grid>
        </Box>
      )}
    </Paper>
  );
};

export default ForecastChart;
