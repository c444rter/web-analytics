// hooks/useHistoricalUploads.js
import { useQuery } from "@tanstack/react-query";
import api from "../lib/api";  // Ensure the API client is in the lib folder

const fetchHistoricalUploads = async () => {
  const response = await api.get("/uploads/history");
  return Array.isArray(response.data) ? response.data : response.data.uploads;
};

const useHistoricalUploads = () => {
  return useQuery(["historicalUploads"], fetchHistoricalUploads, {
    staleTime: 300 * 1000,
    refetchOnWindowFocus: false
  });
};

export default useHistoricalUploads;
