// hooks/useAnalyticsCustom.js
import { useMutation } from "@tanstack/react-query";
import api from "../lib/api";

async function postAnalyticsCustom({ uploadId, selectedMetrics }) {
  // body is an array of aggregator keys: ["orders_summary", "time_series", ...]
  const res = await api.post(`/analytics/custom?upload_id=${uploadId}`, selectedMetrics);
  return res.data; 
  // shape: { "orders_summary": {...}, "time_series": [...], ...} for each requested KPI
}

export default function useAnalyticsCustom() {
  return useMutation(postAnalyticsCustom);
}
