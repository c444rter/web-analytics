// hooks/useProjections.js
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "../lib/api";

// Default fallback data for available models
const fallbackModels = [
  {
    id: "naive",
    name: "Naive Seasonal Model",
    description: "Simple forecasting based on historical averages by day of week"
  },
  {
    id: "arima",
    name: "ARIMA Model",
    description: "Auto-Regressive Integrated Moving Average statistical model"
  }
];

// Default fallback data for forecast
const createFallbackForecast = (days = 30) => {
  const forecast = [];
  const startDate = new Date();
  
  for (let i = 0; i < days; i++) {
    const date = new Date(startDate);
    date.setDate(date.getDate() + i);
    
    forecast.push({
      date: date.toISOString().split('T')[0],
      predicted_orders: 0,
      predicted_revenue: 0,
      confidence_lower: 0,
      confidence_upper: 0
    });
  }
  
  return {
    forecast: {
      forecast,
      metrics: {
        mean_orders: 0,
        mean_revenue: 0,
        total_days_analyzed: 0
      }
    }
  };
};

// Default fallback data for style forecast
const createFallbackStyleForecast = (days = 30) => {
  const forecast = [];
  const startDate = new Date();
  const styles = ["Style A", "Style B"];
  
  for (let i = 0; i < days; i++) {
    const date = new Date(startDate);
    date.setDate(date.getDate() + i);
    
    for (const style of styles) {
      forecast.push({
        date: date.toISOString().split('T')[0],
        style,
        predicted_quantity: 0,
        predicted_revenue: 0
      });
    }
  }
  
  return {
    forecast: {
      forecast,
      styles,
      style_metrics: styles.map(style => ({
        style,
        mean_quantity: 0,
        mean_revenue: 0,
        total_days_analyzed: 0
      })),
      overall_metrics: {
        mean_quantity: 0,
        mean_revenue: 0,
        total_days_analyzed: 0
      }
    }
  };
};

// Fetch available forecasting models
const fetchAvailableModels = (queryClient) => async () => {
  try {
    const res = await api.get("/projections/models");
    return res.data;
  } catch (error) {
    console.error("Error fetching available models:", error);
    
    // Check if we have cached data to return as fallback
    const cachedData = queryClient.getQueryData(["projectionModels"]);
    if (cachedData) {
      console.log("Using cached models data as fallback");
      return cachedData;
    }
    
    // If it's a network error, return a basic fallback structure
    if (!error.response) {
      console.log("Network error, using fallback models");
      return fallbackModels;
    }
    
    // For other errors, throw to be handled by the query's onError
    throw error;
  }
};

// Fetch forecast for a specific upload
const fetchForecast = (queryClient) => async ({ queryKey }) => {
  const [_key, { uploadId, days, model, refreshCache }] = queryKey;
  
  try {
    const params = {
      upload_id: uploadId,
      days,
      model,
    };
    
    if (refreshCache) {
      params.refresh_cache = true;
    }
    
    const res = await api.get("/projections/forecast", { params });
    return res.data;
  } catch (error) {
    console.error("Error fetching forecast:", error);
    
    // Check if we have cached data to return as fallback
    const cachedData = queryClient.getQueryData(["forecast", { uploadId, days, model }]);
    if (cachedData) {
      console.log("Using cached forecast data as fallback");
      return cachedData;
    }
    
    // If it's a network error, return a basic fallback structure
    if (!error.response) {
      console.log("Network error, using fallback forecast");
      return createFallbackForecast(days);
    }
    
    // For other errors, throw to be handled by the query's onError
    throw error;
  }
};

// Fetch style forecast for a specific upload
const fetchStyleForecast = (queryClient) => async ({ queryKey }) => {
  const [_key, { uploadId, days, model, refreshCache }] = queryKey;
  
  try {
    const params = {
      upload_id: uploadId,
      days,
      model,
    };
    
    if (refreshCache) {
      params.refresh_cache = true;
    }
    
    const res = await api.get("/projections/style-forecast", { params });
    return res.data;
  } catch (error) {
    console.error("Error fetching style forecast:", error);
    
    // Check if we have cached data to return as fallback
    const cachedData = queryClient.getQueryData(["styleForecast", { uploadId, days, model }]);
    if (cachedData) {
      console.log("Using cached style forecast data as fallback");
      return cachedData;
    }
    
    // If it's a network error, return a basic fallback structure
    if (!error.response) {
      console.log("Network error, using fallback style forecast");
      return createFallbackStyleForecast(days);
    }
    
    // For other errors, throw to be handled by the query's onError
    throw error;
  }
};

// Hook for fetching available forecasting models
export function useAvailableModels() {
  const queryClient = useQueryClient();
  
  return useQuery(["projectionModels"], fetchAvailableModels(queryClient), {
    staleTime: 1000 * 60 * 60 * 24, // 24 hours
    cacheTime: 1000 * 60 * 60 * 24 * 7, // 7 days
    refetchOnMount: false,
    refetchOnWindowFocus: false,
    retry: 3, // Retry failed requests 3 times
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000), // Exponential backoff
    onError: (error) => {
      console.error("Available models query error:", error);
    },
    // If we have an error but also have data (from fallback), don't show loading state
    keepPreviousData: true
  });
}

// Hook for fetching forecast data
export function useForecast(uploadId, days = 30, model = "naive", enabled = true) {
  const queryClient = useQueryClient();
  
  const query = useQuery(
    ["forecast", { uploadId, days, model }],
    fetchForecast(queryClient),
    {
      enabled: !!uploadId && enabled,
      staleTime: 1000 * 60 * 30, // 30 minutes
      cacheTime: 1000 * 60 * 60 * 24, // 24 hours
      retry: 3, // Retry failed requests 3 times
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000), // Exponential backoff
      onError: (error) => {
        console.error("Forecast query error:", error);
      },
      // If we have an error but also have data (from fallback), don't show loading state
      keepPreviousData: true
    }
  );
  
  // Function to force refresh the forecast
  const refreshForecast = async () => {
    if (!uploadId) return;
    
    try {
      // Use fetchQuery to force a refresh
      const data = await queryClient.fetchQuery(
        ["forecast", { uploadId, days, model, refreshCache: true }],
        fetchForecast(queryClient)
      );
      
      return data;
    } catch (error) {
      console.error("Error refreshing forecast:", error);
      
      // Return the existing data if available
      const cachedData = queryClient.getQueryData(["forecast", { uploadId, days, model }]);
      if (cachedData) {
        return cachedData;
      }
      
      // If no cached data, return fallback
      return createFallbackForecast(days);
    }
  };
  
  return {
    ...query,
    refreshForecast,
    // Add a helper to check if we're using fallback data
    isFallbackData: query.isError && query.data !== undefined
  };
}

// Hook for fetching style-based forecast data
export function useStyleForecast(uploadId, days = 30, model = "naive", enabled = true) {
  const queryClient = useQueryClient();
  
  const query = useQuery(
    ["styleForecast", { uploadId, days, model }],
    fetchStyleForecast(queryClient),
    {
      enabled: !!uploadId && enabled,
      staleTime: 1000 * 60 * 30, // 30 minutes
      cacheTime: 1000 * 60 * 60 * 24, // 24 hours
      retry: 3, // Retry failed requests 3 times
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000), // Exponential backoff
      onError: (error) => {
        console.error("Style forecast query error:", error);
      },
      // If we have an error but also have data (from fallback), don't show loading state
      keepPreviousData: true
    }
  );
  
  // Function to force refresh the style forecast
  const refreshStyleForecast = async () => {
    if (!uploadId) return;
    
    try {
      // Use fetchQuery to force a refresh
      const data = await queryClient.fetchQuery(
        ["styleForecast", { uploadId, days, model, refreshCache: true }],
        fetchStyleForecast(queryClient)
      );
      
      return data;
    } catch (error) {
      console.error("Error refreshing style forecast:", error);
      
      // Return the existing data if available
      const cachedData = queryClient.getQueryData(["styleForecast", { uploadId, days, model }]);
      if (cachedData) {
        return cachedData;
      }
      
      // If no cached data, return fallback
      return createFallbackStyleForecast(days);
    }
  };
  
  return {
    ...query,
    refreshStyleForecast,
    // Add a helper to check if we're using fallback data
    isFallbackData: query.isError && query.data !== undefined
  };
}

// Default export for backward compatibility
export default useForecast;
