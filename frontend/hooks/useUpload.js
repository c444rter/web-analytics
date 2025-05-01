// hooks/useUpload.js
import { useMutation } from "@tanstack/react-query";
import api from "../lib/api";  // Updated import path

// Function to handle the file upload process.
const uploadFile = async (formData) => {
  try {
    const response = await api.post("/uploads/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
      // Add timeout specifically for uploads which can take longer
      timeout: 60000, // 60 seconds
      // Add onUploadProgress handler for tracking upload progress
      onUploadProgress: (progressEvent) => {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        // You could dispatch this to a state manager or callback if needed
        console.log(`Upload progress: ${percentCompleted}%`);
        
        // Store progress in a global variable that the component can access
        window.uploadProgress = percentCompleted;
      }
    });
    return response.data;
  } catch (error) {
    console.error("Error uploading file:", error);
    
    // Create a more user-friendly error message based on the error type
    let errorMessage = "An error occurred during file upload.";
    
    if (!error.response) {
      // Network error
      errorMessage = "Network error. Please check your internet connection and try again.";
    } else if (error.response.status === 413) {
      // File too large
      errorMessage = "The file is too large. Please upload a smaller file.";
    } else if (error.response.status === 415) {
      // Unsupported file type
      errorMessage = "Unsupported file type. Please upload a CSV or Excel file.";
    } else if (error.response.status === 400) {
      // Bad request - likely invalid file format
      errorMessage = "Invalid file format. Please ensure your file contains the required data.";
    } else if (error.response.status === 401) {
      // Unauthorized
      errorMessage = "You need to be logged in to upload files.";
    } else if (error.response.status >= 500) {
      // Server error
      errorMessage = "Server error. Please try again later.";
    }
    
    // Enhance the error object with our custom message
    const enhancedError = new Error(errorMessage);
    enhancedError.originalError = error;
    enhancedError.status = error.response?.status;
    enhancedError.isUploadError = true;
    
    throw enhancedError;
  }
};

// Custom mutation hook to handle file uploads.
const useUpload = () => {
  return useMutation(uploadFile, {
    retry: (failureCount, error) => {
      // Don't retry for client errors (4xx) or if we've already tried 3 times
      if (error.status >= 400 && error.status < 500) return false;
      return failureCount < 3;
    },
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000), // Exponential backoff
    onError: (error) => {
      console.error("Upload mutation error:", error);
      // You could add additional error handling here if needed
    }
  });
};

export default useUpload;
