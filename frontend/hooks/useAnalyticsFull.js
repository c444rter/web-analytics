// hooks/useAnalyticsFull.js
import { useQuery } from "@tanstack/react-query";
import api from "../lib/api";

async function fetchAnalyticsFull(uploadId) {
  const res = await api.get("/analytics/full", { params: { upload_id: uploadId } });
  return res.data; 
  // shape: { orders_summary: {...}, time_series: [...], top_products_by_quantity: [...], etc. }
}

export default function useAnalyticsFull(uploadId, enabled = true) {
  return useQuery(["analyticsFull", uploadId], () => fetchAnalyticsFull(uploadId), {
    enabled: !!uploadId && enabled,
  });
}
