// hooks/useUserDetails.js
import { useQuery } from "@tanstack/react-query";
import { useSession } from "next-auth/react";
import api from "../lib/api";

// Create a fallback user details object based on session data
const createFallbackUserDetails = (session) => {
  return {
    email: session?.user?.email || "user@example.com",
    username: session?.user?.username || session?.user?.name || "User", // Prioritize username field
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    is_fallback: true // Flag to indicate this is fallback data
  };
};

async function fetchUserDetails() {
  try {
    const response = await api.get("/users/me");
    return response.data;
  } catch (error) {
    console.error("Error fetching user details:", error);
    
    // If there's no response (network error)
    if (!error.response) {
      console.warn("Network error when fetching user details. Using fallback data.");
      // Get session data from next-auth
      const session = typeof window !== 'undefined' ? JSON.parse(localStorage.getItem('next-auth.session-token') || '{}') : {};
      return createFallbackUserDetails(session);
    }
    
    // If the endpoint is not found (404), return a fallback object with session data
    if (error.response.status === 404) {
      console.warn("The /users/me endpoint is not available. Using session data as fallback.");
      // Get session data from localStorage or sessionStorage if available
      const session = typeof window !== 'undefined' ? JSON.parse(localStorage.getItem('next-auth.session-token') || '{}') : {};
      return createFallbackUserDetails(session);
    }
    
    // If unauthorized (401), return a fallback with minimal data
    if (error.response.status === 401) {
      console.warn("Unauthorized when fetching user details. User may need to log in again.");
      return {
        email: "guest@example.com",
        username: "Guest",
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        is_fallback: true,
        auth_error: true
      };
    }
    
    // For other errors, rethrow
    throw error;
  }
}

export default function useUserDetails() {
  const { data: session, status } = useSession();
  
  return useQuery(
    ["userDetails"],
    fetchUserDetails,
    {
      // Only fetch if the user is authenticated
      enabled: status === "authenticated",
      // Cache the data for 5 minutes
      staleTime: 1000 * 60 * 5,
      // Keep in cache for 1 hour
      cacheTime: 1000 * 60 * 60,
      // Retry with exponential backoff
      retry: (failureCount, error) => {
        // Don't retry for 404 or 401 errors
        if (error.response && (error.response.status === 404 || error.response.status === 401)) {
          return false;
        }
        // Retry up to 3 times for other errors
        return failureCount < 3;
      },
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000), // Exponential backoff
      // Handle errors
      onError: (error) => {
        console.error("Error fetching user details:", error);
      },
      // Fallback data if the query fails
      placeholderData: createFallbackUserDetails(session),
      // If we have an error but also have data (from fallback), don't show loading state
      keepPreviousData: true
    }
  );
}
