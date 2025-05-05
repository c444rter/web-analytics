// lib/api.js
import axios from "axios";
import { toast } from "react-toastify"; // optional: for notifications

const api = axios.create({
  // Use relative URLs to leverage Next.js rewrites
  baseURL: "/",
  timeout: 15000, // 15 second timeout
  // Add retry logic for network issues
  retry: 3,
  retryDelay: (retryCount) => {
    return retryCount * 1000; // 1s, 2s, 3s
  }
});

// Add request interceptor to attach auth token
api.interceptors.request.use((config) => {
  // Try to get token from localStorage only (avoid async session fetching)
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  
  return config;
}, (error) => {
  // Handle request errors
  console.error("Request error:", error);
  if (typeof window !== "undefined" && toast) {
    toast.error("Error preparing request. Please check your connection.");
  }
  return Promise.reject(error);
});

// Response interceptor with comprehensive error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Initialize retry logic for network errors
    const config = error.config || {};
    
    // If it's a network error, timeout, or 5xx error, retry the request
    if (
      (error.code === 'ECONNABORTED' || 
       !error.response || 
       error.response.status >= 500) && 
      config.retry
    ) {
      // Set the retry count
      config.retryCount = config.retryCount || 0;
      
      // Check if we've maxed out the retries
      if (config.retryCount < config.retry) {
        // Increase the retry count
        config.retryCount += 1;
        
        // Create a new promise to handle the retry
        return new Promise((resolve) => {
          // Show retry toast if available
          if (typeof window !== "undefined" && toast) {
            toast.info(`Connection issue detected. Retrying (${config.retryCount}/${config.retry})...`);
          }
          
          // Set a timeout to retry the request
          setTimeout(() => {
            resolve(api(config));
          }, config.retryDelay(config.retryCount));
        });
      }
    }
    
    // Handle specific error types with user-friendly messages
    if (!error.response) {
      // Network error
      console.error("Network Error:", error);
      if (typeof window !== "undefined" && toast) {
        toast.error("Network error. Please check your internet connection.");
      }
    } else {
      // Server returned an error response
      const status = error.response.status;
      
      if (status === 401) {
        // Unauthorized - redirect to login
        console.error("Unauthorized:", error);
        if (typeof window !== "undefined") {
          window.location.href = "/login";
        }
        if (typeof window !== "undefined" && toast) {
          toast.error("Your session has expired. Please log in again.");
        }
      } else if (status === 403) {
        // Forbidden
        console.error("Forbidden:", error);
        if (typeof window !== "undefined" && toast) {
          toast.error("You don't have permission to access this resource.");
        }
      } else if (status === 404) {
        // Not found
        console.error("Not Found:", error);
        if (typeof window !== "undefined" && toast) {
          toast.error("The requested resource was not found.");
        }
      } else if (status >= 500) {
        // Server error
        console.error("Server Error:", error);
        if (typeof window !== "undefined" && toast) {
          toast.error("Server error. Please try again later.");
        }
      } else {
        // Other errors
        console.error("API Error:", error);
        const errorMessage = error.response.data?.detail || error.response.data?.message || "An error occurred";
        if (typeof window !== "undefined" && toast) {
          toast.error(`Error: ${errorMessage}`);
        }
      }
    }
    
    return Promise.reject(error);
  }
);

// Add a method to check API health
api.checkHealth = async () => {
  try {
    const response = await api.get('/health', { timeout: 5000 });
    return response.data;
  } catch (error) {
    console.error("API Health Check Failed:", error);
    return { status: 'error', message: 'API is unreachable' };
  }
};

export default api;
