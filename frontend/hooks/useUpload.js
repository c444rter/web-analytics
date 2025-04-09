// hooks/useUpload.js
import { useMutation } from "@tanstack/react-query";
import api from "../lib/api";  // Updated import path

// Function to handle the file upload process.
const uploadFile = async (formData) => {
  const response = await api.post("/uploads/", formData, {
    headers: { "Content-Type": "multipart/form-data" }
  });
  return response.data;
};

// Custom mutation hook to handle file uploads.
const useUpload = () => {
  return useMutation(uploadFile);
};

export default useUpload;
