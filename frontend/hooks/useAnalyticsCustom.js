// hooks/useAnalyticsCustom.js
import { useMutation, useQueryClient } from "@tanstack/react-query";
import api from "../lib/api";

// Default fallback data for custom analytics
const createFallbackCustomAnalytics = (selectedMetrics) => {
  const result = {};
  
  if (selectedMetrics.includes("orders_summary")) {
    result.orders_summary = {
      total_orders: 0,
      total_revenue: 0,
      average_order_value: 0,
      total_customers: 0,
      repeat_customer_rate: 0
    };
  }
  
  if (selectedMetrics.includes("time_series")) {
    result.time_series = Array.from({ length: 30 }, (_, i) => {
      const date = new Date();
      date.setDate(date.getDate() - 30 + i);
      return {
        date: date.toISOString().split('T')[0],
        orders: 0,
        revenue: 0
      };
    });
  }
  
  if (selectedMetrics.includes("top_products_by_quantity")) {
    result.top_products_by_quantity = [];
  }
  
  if (selectedMetrics.includes("top_products_by_revenue")) {
    result.top_products_by_revenue = [];
  }
  
  if (selectedMetrics.includes("geographic_distribution")) {
    result.geographic_distribution = [];
  }
  
  result.is_fallback = true;
  
  return result;
};

async function postAnalyticsCustom(queryClient, { uploadId, selectedMetrics, refreshCache = false }) {
  try {
    // body is an array of aggregator keys: ["orders_summary", "time_series", ...]
    const res = await api.post(
      `/analytics/custom?upload_id=${uploadId}&refresh_cache=${refreshCache}`, 
      selectedMetrics
    );
    return res.data; 
    // shape: { "orders_summary": {...}, "time_series": [...], ...} for each requested KPI
  } catch (error) {
    console.error("Error fetching custom analytics:", error);
    
    // Try to get cached data for this specific custom query
    const cacheKey = JSON.stringify({ uploadId, selectedMetrics });
    const cachedData = queryClient.getQueryData(["analyticsCustom", cacheKey]);
    
    if (cachedData) {
      console.log("Using cached custom analytics data as fallback");
      return cachedData;
    }
    
    // For any error, return fallback data to ensure the UI remains functional
    console.log("Error fetching custom analytics, using fallback data:", error.message);
    return {
      ...createFallbackCustomAnalytics(selectedMetrics),
      is_fallback: true,
      connection_error: true,
      error_message: error.message
    };
  }
}

export default function useAnalyticsCustom() {
  const queryClient = useQueryClient();
  
  const mutation = useMutation(
    (variables) => postAnalyticsCustom(queryClient, variables),
    {
      // When the mutation succeeds, invalidate any queries that might be affected
      onSuccess: (data, variables) => {
        // Invalidate the full analytics query for this upload
        queryClient.invalidateQueries(["analyticsFull", variables.uploadId]);
        
        // Cache this custom query result for potential fallback
        const cacheKey = JSON.stringify({ 
          uploadId: variables.uploadId, 
          selectedMetrics: variables.selectedMetrics 
        });
        queryClient.setQueryData(["analyticsCustom", cacheKey], data);
      },
      onError: (error, variables) => {
        console.error("Custom analytics mutation error:", error);
        
        // If it's a network error, provide fallback data
        if (!error.response) {
          const fallbackData = createFallbackCustomAnalytics(variables.selectedMetrics);
          
          // Cache the fallback data
          const cacheKey = JSON.stringify({ 
            uploadId: variables.uploadId, 
            selectedMetrics: variables.selectedMetrics 
          });
          queryClient.setQueryData(["analyticsCustom", cacheKey], fallbackData);
          
          // Return the fallback data
          return fallbackData;
        }
      },
      retry: 3, // Retry failed requests 3 times
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000), // Exponential backoff
    }
  );
  
  // Add a function to force refresh the cache
  const fetchWithRefresh = async (variables) => {
    try {
      return await mutation.mutateAsync({
        ...variables,
        refreshCache: true
      });
    } catch (error) {
      console.error("Error refreshing custom analytics:", error);
      
      // Try to return cached data if available
      const cacheKey = JSON.stringify({ 
        uploadId: variables.uploadId, 
        selectedMetrics: variables.selectedMetrics 
      });
      const cachedData = queryClient.getQueryData(["analyticsCustom", cacheKey]);
      
      if (cachedData) {
        console.log("Using cached data after refresh failure");
        return cachedData;
      }
      
      // If no cached data, return fallback
      return createFallbackCustomAnalytics(variables.selectedMetrics);
    }
  };
  
  return {
    ...mutation,
    fetchWithRefresh,
    // Add a helper to check if we're using fallback data
    isFallbackData: (mutation.isError && mutation.data !== undefined) ||
                    (mutation.data && mutation.data.is_fallback === true)
  };
}
