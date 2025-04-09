// hooks/useAnalyticsAvailable.js
import { useQuery } from "@tanstack/react-query";
import api from "../lib/api"; // an axios or fetch wrapper

async function fetchAnalyticsAvailable() {
  const res = await api.get("/analytics/available");
  return res.data; // array of objects: [{ key, label, description }, ...]
}

export default function useAnalyticsAvailable() {
  return useQuery(["analyticsAvailable"], fetchAnalyticsAvailable);
}
