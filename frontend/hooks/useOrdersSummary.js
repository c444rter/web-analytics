// hooks/useOrdersSummary.js
import { useQuery } from "@tanstack/react-query";
import api from "../lib/api";  // Ensure this path is correct based on your folder structure

// Fetch orders summary for a specific upload.
const fetchOrdersSummary = async ({ queryKey }) => {
  const [_key, { uploadId, startDate, endDate }] = queryKey;
  const params = {};
  if (uploadId) params.upload_id = uploadId;
  if (startDate) params.start_date = startDate;
  if (endDate) params.end_date = endDate;
  
  const response = await api.get("/dashboard/orders-summary", { params });
  return response.data;
};

const useOrdersSummary = (uploadId, startDate = null, endDate = null) => {
  return useQuery(
    ["ordersSummary", { uploadId, startDate, endDate }],
    fetchOrdersSummary,
    {
      staleTime: 300 * 1000, // Cache for 5 minutes.
      refetchOnWindowFocus: false,
    }
  );
};

export default useOrdersSummary;
