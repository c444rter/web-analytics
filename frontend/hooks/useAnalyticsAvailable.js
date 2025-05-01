// hooks/useAnalyticsAvailable.js
import { useQuery, useQueryClient } from "@tanstack/react-query";
import api from "../lib/api"; // an axios or fetch wrapper

// Default fallback data in case of network errors
const fallbackAvailableMetrics = [
  { 
    key: "orders_summary", 
    label: "Orders Summary", 
    description: "Overview of order counts and revenue" 
  },
  { 
    key: "time_series", 
    label: "Time Series", 
    description: "Orders and revenue over time" 
  },
  { 
    key: "top_products_by_quantity", 
    label: "Top Products by Quantity", 
    description: "Most sold products by quantity" 
  },
  { 
    key: "top_products_by_revenue", 
    label: "Top Products by Revenue", 
    description: "Most profitable products by revenue" 
  }
];

const fetchAnalyticsAvailable = (queryClient) => async () => {
  try {
    const res = await api.get("/analytics/available");
    return res.data; // array of objects: [{ key, label, description }, ...]
  } catch (error) {
    console.error("Error fetching available analytics:", error);
    
    // Check if we have cached data to return as fallback
    const cachedData = queryClient.getQueryData(["analyticsAvailable"]);
    if (cachedData) {
      console.log("Using cached available metrics data as fallback");
      return cachedData;
    }
    
    // Return fallback data if we can't reach the server
    if (!error.response) {
      console.log("Network error, using fallback available metrics");
      return fallbackAvailableMetrics;
    }
    
    // For other errors, throw to be handled by the query's onError
    throw error;
  }
}

export default function useAnalyticsAvailable(enabled = true) {
  const queryClient = useQueryClient();
  
  return useQuery(["analyticsAvailable"], fetchAnalyticsAvailable(queryClient), {
    enabled,
    // This data rarely changes, so we can cache it for longer
    staleTime: 1000 * 60 * 60 * 24, // 24 hours
    cacheTime: 1000 * 60 * 60 * 24 * 7, // 7 days
    refetchOnMount: false,
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
    retry: 3, // Retry failed requests 3 times
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000), // Exponential backoff
    onError: (error) => {
      console.error("Available analytics query error:", error);
    },
    // If we have an error but also have data (from fallback), don't show loading state
    keepPreviousData: true
  });
}
