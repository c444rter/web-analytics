// hooks/useAnalyticsFull.js
import { useQuery, useQueryClient } from "@tanstack/react-query";
import api from "../lib/api";

// Default fallback data for analytics
const createFallbackAnalytics = () => {
  return {
    orders_summary: {
      total_orders: 0,
      total_revenue: 0,
      average_order_value: 0,
      total_customers: 0,
      repeat_customer_rate: 0
    },
    time_series: Array.from({ length: 30 }, (_, i) => {
      const date = new Date();
      date.setDate(date.getDate() - 30 + i);
      return {
        date: date.toISOString().split('T')[0],
        orders: 0,
        revenue: 0
      };
    }),
    top_products_by_quantity: [],
    top_products_by_revenue: [],
    geographic_distribution: [],
    is_fallback: true
  };
};

// This function is used inside the useQuery hook
const fetchAnalyticsFull = (queryClient) => async ({ queryKey }) => {
  const [_key, uploadId, refreshCache = false] = queryKey;
  
  try {
    const res = await api.get("/analytics/full", { 
      params: { 
        upload_id: uploadId,
        refresh_cache: refreshCache 
      } 
    });
    return res.data; 
    // shape: { orders_summary: {...}, time_series: [...], top_products_by_quantity: [...], etc. }
  } catch (error) {
    console.error("Error fetching analytics data:", error);
    
    // Check if we have cached data to return as fallback
    const cachedData = queryClient.getQueryData(["analyticsFull", uploadId]);
    if (cachedData) {
      console.log("Using cached analytics data as fallback");
      return cachedData;
    }
    
    // If it's a network error, CORS error, or any other error, return a basic fallback structure
    // This ensures we always have fallback data to display
    console.log("Error fetching analytics data, using fallback analytics data:", error.message);
    return {
      ...createFallbackAnalytics(),
      is_fallback: true,
      connection_error: true,
      error_message: error.message
    };
    
    // For other errors, throw to be handled by the query's onError
    throw error;
  }
};

export default function useAnalyticsFull(uploadId, enabled = true) {
  const queryClient = useQueryClient();
  
  const query = useQuery(
    ["analyticsFull", uploadId], 
    fetchAnalyticsFull(queryClient), 
    {
      enabled: !!uploadId && enabled,
      staleTime: 1000 * 60 * 60, // 1 hour
      cacheTime: 1000 * 60 * 60 * 24, // 24 hours
      retry: 3, // Retry failed requests 3 times
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000), // Exponential backoff
      onError: (error) => {
        console.error("Analytics query error:", error);
      },
      // If we have an error but also have data (from fallback), don't show loading state
      keepPreviousData: true,
      // Provide fallback data if nothing else is available
      placeholderData: createFallbackAnalytics()
    }
  );
  
  // Add a refresh function that forces a cache refresh
  const refreshAnalytics = async () => {
    if (!uploadId) return;
    
    try {
      // Fetch with refresh_cache=true
      const data = await queryClient.fetchQuery(
        ["analyticsFull", uploadId, true],
        fetchAnalyticsFull(queryClient)
      );
      
      return data;
    } catch (error) {
      console.error("Error refreshing analytics:", error);
      
      // Return the existing data if available
      const cachedData = queryClient.getQueryData(["analyticsFull", uploadId]);
      if (cachedData) {
        return cachedData;
      }
      
      // If no cached data, return fallback
      return createFallbackAnalytics();
    }
  };
  
  return {
    ...query,
    refreshAnalytics,
    // Add a helper to check if we're using fallback data
    isFallbackData: (query.isError && query.data !== undefined) || 
                    (query.data && query.data.is_fallback === true)
  };
}
