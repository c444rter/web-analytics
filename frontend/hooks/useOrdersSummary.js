// hooks/useOrdersSummary.js
import { useQuery, useQueryClient } from "@tanstack/react-query";
import api from "../lib/api";  // Ensure this path is correct based on your folder structure

// Default fallback data for orders summary
const fallbackOrdersSummary = {
  total_orders: 0,
  total_revenue: 0,
  average_order_value: 0,
  total_customers: 0,
  repeat_customer_rate: 0,
  top_products: [],
  recent_orders: []
};

// Fetch orders summary for a specific upload.
const fetchOrdersSummary = async ({ queryKey }) => {
  const [_key, { uploadId, startDate, endDate, refreshCache }] = queryKey;
  
  try {
    const params = {};
    if (uploadId) params.upload_id = uploadId;
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    if (refreshCache) params.refresh_cache = refreshCache;
    
    const response = await api.get("/dashboard/orders-summary", { params });
    return response.data;
  } catch (error) {
    console.error("Error fetching orders summary:", error);
    
    // Check if we have cached data to return as fallback
    if (error.config?.retryCount > 0) {
      const queryClient = new useQueryClient();
      const cachedData = queryClient.getQueryData(["ordersSummary", { uploadId, startDate, endDate }]);
      
      if (cachedData) {
        console.log("Using cached orders summary data as fallback");
        return cachedData;
      }
    }
    
    // If it's a network error, return a basic fallback structure
    if (!error.response) {
      console.log("Network error, using fallback orders summary");
      return fallbackOrdersSummary;
    }
    
    // For other errors, throw to be handled by the query's onError
    throw error;
  }
};

const useOrdersSummary = (uploadId, startDate = null, endDate = null) => {
  const queryClient = useQueryClient();
  
  const query = useQuery(
    ["ordersSummary", { uploadId, startDate, endDate }],
    fetchOrdersSummary,
    {
      staleTime: 1000 * 60 * 30, // Cache for 30 minutes
      cacheTime: 1000 * 60 * 60, // Keep in cache for 1 hour
      refetchOnWindowFocus: false,
      enabled: !!uploadId, // Only run the query if uploadId is provided
      retry: 3, // Retry failed requests 3 times
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000), // Exponential backoff
      onError: (error) => {
        console.error("Orders summary query error:", error);
      },
      // If we have an error but also have data (from fallback), don't show loading state
      keepPreviousData: true
    }
  );
  
  // Add a refresh function that forces a cache refresh
  const refreshSummary = async () => {
    if (!uploadId) return;
    
    try {
      // Fetch with refresh_cache=true
      const data = await fetchOrdersSummary({ 
        queryKey: ["ordersSummary", { uploadId, startDate, endDate, refreshCache: true }] 
      });
      
      // Update the cache with the new data
      queryClient.setQueryData(
        ["ordersSummary", { uploadId, startDate, endDate }], 
        data
      );
      
      return data;
    } catch (error) {
      console.error("Error refreshing orders summary:", error);
      
      // Return the existing data if available
      const cachedData = queryClient.getQueryData(["ordersSummary", { uploadId, startDate, endDate }]);
      if (cachedData) {
        return cachedData;
      }
      
      // If no cached data, return fallback
      return fallbackOrdersSummary;
    }
  };
  
  return {
    ...query,
    refreshSummary,
    // Add a helper to check if we're using fallback data
    isFallbackData: query.isError && query.data !== undefined
  };
};

export default useOrdersSummary;
