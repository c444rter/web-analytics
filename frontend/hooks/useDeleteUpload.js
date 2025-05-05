// hooks/useDeleteUpload.js
import { useMutation, useQueryClient } from "@tanstack/react-query";
import api from "../lib/api";

/**
 * Delete an upload by ID
 * @param {number} uploadId - The ID of the upload to delete
 * @returns {Promise} - Promise that resolves when the upload is deleted
 */
const deleteUpload = async (uploadId) => {
  try {
    const response = await api.delete(`/uploads/${uploadId}`);
    return response.data;
  } catch (error) {
    console.error("Error deleting upload:", error);
    
    // Create a more user-friendly error message based on the error type
    let errorMessage = "An error occurred while deleting the upload.";
    
    if (!error.response) {
      // Network error
      errorMessage = "Network error. Please check your internet connection and try again.";
    } else if (error.response.status === 404) {
      // Upload not found
      errorMessage = "The upload could not be found or may have already been deleted.";
    } else if (error.response.status === 401 || error.response.status === 403) {
      // Unauthorized or forbidden
      errorMessage = "You don't have permission to delete this upload.";
    } else if (error.response.status >= 500) {
      // Server error
      errorMessage = "Server error. Please try again later.";
    }
    
    // Enhance the error object with our custom message
    const enhancedError = new Error(errorMessage);
    enhancedError.originalError = error;
    enhancedError.status = error.response?.status;
    enhancedError.isDeleteError = true;
    
    throw enhancedError;
  }
};

/**
 * Custom hook for deleting uploads
 * @returns {Object} - Mutation object with mutate function and status
 */
const useDeleteUpload = () => {
  const queryClient = useQueryClient();
  
  return useMutation(deleteUpload, {
    // When the mutation is successful, invalidate the historicalUploads query
    // to refetch the uploads list
    onSuccess: () => {
      queryClient.invalidateQueries(["historicalUploads"]);
    },
    // Retry logic for network errors, but not for client errors
    retry: (failureCount, error) => {
      // Don't retry for client errors (4xx) or if we've already tried 2 times
      if (error.status >= 400 && error.status < 500) return false;
      return failureCount < 2;
    },
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 10000), // Exponential backoff
    onError: (error) => {
      console.error("Delete mutation error:", error);
      // Additional error handling can be added here if needed
    }
  });
};

export default useDeleteUpload;
