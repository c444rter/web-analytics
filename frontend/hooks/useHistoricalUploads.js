// hooks/useHistoricalUploads.js
import { useQuery, useQueryClient } from "@tanstack/react-query";
import api from "../lib/api";  // Ensure the API client is in the lib folder

// Default fallback data for historical uploads
const fallbackUploads = [
  {
    id: -1,
    file_name: "Sample Data (Offline Mode)",
    uploaded_at: new Date().toISOString(),
    status: "completed",
    file_size: 0,
    row_count: 0
  }
];

const fetchHistoricalUploads = (queryClient) => async () => {
  try {
    const response = await api.get("/uploads/history");
    return Array.isArray(response.data) ? response.data : response.data.uploads;
  } catch (error) {
    console.error("Error fetching historical uploads:", error);
    
    // Check if we have cached data to return as fallback
    const cachedData = queryClient.getQueryData(["historicalUploads"]);
    
    if (cachedData) {
      console.log("Using cached historical uploads data as fallback");
      return cachedData;
    }
    
    // If it's a network error, return a basic fallback structure
    if (!error.response) {
      console.log("Network error, using fallback uploads");
      return fallbackUploads;
    }
    
    // For other errors, throw to be handled by the query's onError
    throw error;
  }
};

const useHistoricalUploads = () => {
  const queryClient = useQueryClient();
  
  const query = useQuery(["historicalUploads"], fetchHistoricalUploads(queryClient), {
    staleTime: 300 * 1000, // 5 minutes
    cacheTime: 1000 * 60 * 60, // 1 hour
    refetchOnWindowFocus: false,
    retry: 3, // Retry failed requests 3 times
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000), // Exponential backoff
    onError: (error) => {
      console.error("Historical uploads query error:", error);
    },
    // If we have an error but also have data (from fallback), don't show loading state
    keepPreviousData: true
  });
  
  // Add a refresh function that forces a refetch
  const refetch = async () => {
    try {
      return await queryClient.fetchQuery(["historicalUploads"]);
    } catch (error) {
      console.error("Error refreshing historical uploads:", error);
      
      // Return the existing data if available
      const cachedData = queryClient.getQueryData(["historicalUploads"]);
      if (cachedData) {
        return cachedData;
      }
      
      // If no cached data, return fallback
      return fallbackUploads;
    }
  };
  
  return {
    ...query,
    refetch,
    // Add a helper to check if we're using fallback data
    isFallbackData: query.isError && query.data !== undefined
  };
};

export default useHistoricalUploads;
