"use client";

import React, { useState, useEffect } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import {
  Box,
  Typography,
  Button,
  Checkbox,
  FormControlLabel,
  CircularProgress,
  Select,
  MenuItem,
  FormControl,
  InputLabel
} from "@mui/material";

// Aggregator block that references KPICard, KPILineChart, etc.
import AggregatorBlock from "../../components/AggregatorBlock";

// Import your TanStack Query hooks for analytics
import useAnalyticsFull from "../../hooks/useAnalyticsFull";
import useAnalyticsAvailable from "../../hooks/useAnalyticsAvailable";
import useAnalyticsCustom from "../../hooks/useAnalyticsCustom";

// Import your hook to fetch historical uploads
import useHistoricalUploads from "../../hooks/useHistoricalUploads";

export default function DashboardPage() {
  const router = useRouter();
  const searchParams = useSearchParams();

  // Use query params to initialize uploadId and mode
  const initialUploadId = searchParams.get("upload_id") || "";
  const mode = searchParams.get("mode") || "default";

  // State for current upload selection (for historical switching)
  const [uploadId, setUploadId] = useState(initialUploadId);

  // For "historical uploads" switching—fetch past uploads.
  const {
    data: historicalUploads,
    isLoading: loadingHistory,
    isError: errorHistory,
  } = useHistoricalUploads();

  // For "custom" mode, fetch available aggregator keys
  const {
    data: availableMetrics,
    isLoading: loadingAvailable,
    isError: errorAvailable,
  } = useAnalyticsAvailable();

  // For "default" mode, fetch all analytics based on the current uploadId
  const {
    data: fullAnalytics,
    isLoading: loadingFull,
    isError: errorFull,
  } = useAnalyticsFull(uploadId, mode === "default");

  // For "custom" mode, user picks aggregator keys, then calls the custom endpoint
  const [selectedKeys, setSelectedKeys] = useState([]);
  const {
    mutateAsync: fetchCustomAnalytics,
    data: customAnalytics,
    isLoading: loadingCustom,
    isError: errorCustom,
  } = useAnalyticsCustom();

  useEffect(() => {
    if (!uploadId) {
      console.warn("No upload_id found in query params. Please specify ?upload_id=XYZ");
    }
  }, [uploadId]);

  const handleToggleKey = (key) => {
    setSelectedKeys((prev) =>
      prev.includes(key) ? prev.filter((k) => k !== key) : [...prev, key]
    );
  };

  const handleFetchCustom = async () => {
    if (!uploadId || selectedKeys.length === 0) return;
    await fetchCustomAnalytics({ uploadId, selectedMetrics: selectedKeys });
  };

  // When user selects a different historical upload, update state and route
  const handleHistoricalChange = (event) => {
    const newUploadId = event.target.value;
    setUploadId(newUploadId);
    router.push(`/dashboard?upload_id=${newUploadId}&mode=${mode}`);
  };

  // Basic error checks
  if (mode === "default" && errorFull) {
    return <Typography color="error">Error loading full analytics data.</Typography>;
  }
  if (mode === "custom" && errorAvailable) {
    return <Typography color="error">Error loading available metrics.</Typography>;
  }
  if (mode === "custom" && errorCustom) {
    return <Typography color="error">Error calling custom analytics endpoint.</Typography>;
  }
  if (errorHistory) {
    return <Typography color="error">Error loading historical uploads.</Typography>;
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" mb={2}>
        Dashboard (Mode: {mode.toUpperCase()})
      </Typography>

      {/* Historical Upload Selector */}
      <Box sx={{ mb: 3 }}>
        <FormControl fullWidth>
          <InputLabel id="upload-select-label">Select Upload</InputLabel>
          <Select
            labelId="upload-select-label"
            value={uploadId}
            label="Select Upload"
            onChange={handleHistoricalChange}
          >
            {loadingHistory && (
              <MenuItem value="">
                <em>Loading uploads...</em>
              </MenuItem>
            )}
            {historicalUploads &&
              historicalUploads.map((upload) => (
                <MenuItem key={upload.id} value={upload.id}>
                  {upload.file_name} - {new Date(upload.uploaded_at).toLocaleString()} - Status: {upload.status}
                </MenuItem>
              ))}
          </Select>
        </FormControl>
      </Box>

      {/* If no uploadId, prompt user */}
      {!uploadId && (
        <Typography color="error">
          No upload_id specified. Please return to the upload page or select an upload.
        </Typography>
      )}

      {/* =========================
          DEFAULT MODE: full analytics
         ========================= */}
      {mode === "default" && (
        <>
          {loadingFull && (
            <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
              <CircularProgress size={24} />
              <Typography>Loading all KPIs (Full Mode)...</Typography>
            </Box>
          )}
          {fullAnalytics && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="h6">All KPI Results</Typography>
              {Object.entries(fullAnalytics).map(([key, value]) => (
                <AggregatorBlock
                  key={key}
                  aggregatorKey={key}
                  aggregatorData={value}
                />
              ))}
            </Box>
          )}
        </>
      )}

      {/* =========================
          CUSTOM MODE: select KPIs to fetch
         ========================= */}
      {mode === "custom" && (
        <>
          <Typography mb={2}>
            Select which KPI(s) you want, then click "Load Selected KPIs."
          </Typography>

          {loadingAvailable ? (
            <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
              <CircularProgress size={24} />
              <Typography>Loading available metrics...</Typography>
            </Box>
          ) : (
            <Box sx={{ my: 2 }}>
              {availableMetrics?.map((metric) => (
                <FormControlLabel
                  key={metric.key}
                  control={
                    <Checkbox
                      checked={selectedKeys.includes(metric.key)}
                      onChange={() => handleToggleKey(metric.key)}
                    />
                  }
                  label={`${metric.label} – ${metric.description}`}
                />
              ))}
            </Box>
          )}

          <Button
            variant="contained"
            onClick={handleFetchCustom}
            disabled={!uploadId || selectedKeys.length === 0 || loadingCustom}
            sx={{ mb: 2 }}
          >
            Load Selected KPIs
          </Button>

          {loadingCustom && (
            <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
              <CircularProgress size={24} />
              <Typography>Loading custom metrics...</Typography>
            </Box>
          )}
          {customAnalytics && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="h6">Custom KPI Results</Typography>
              {Object.entries(customAnalytics).map(([key, data]) => (
                <AggregatorBlock
                  key={key}
                  aggregatorKey={key}
                  aggregatorData={data}
                />
              ))}
            </Box>
          )}
        </>
      )}
    </Box>
  );
}
