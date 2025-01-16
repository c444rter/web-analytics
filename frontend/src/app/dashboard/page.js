"use client";

import React, { useRef, useEffect } from "react";
import Chart from "chart.js/auto";
import { useSelector } from "react-redux";
import { Container, Typography } from "@mui/material";

export default function DashboardPage() {
  const chartRef = useRef(null);
  const lastUpload = useSelector((state) => state.app.lastUpload);

  useEffect(() => {
    if (!chartRef.current) return;

    const ctx = chartRef.current.getContext("2d");
    new Chart(ctx, {
      type: "bar",
      data: {
        labels: ["A", "B", "C"],
        datasets: [
          { label: "Sample Data", data: [12, 19, 7], backgroundColor: "blue" },
        ],
      },
    });
  }, []);

  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      {lastUpload ? (
        <>
          <Typography variant="body1" sx={{ mb: 1 }}>
            Last upload: <strong>{lastUpload.fileName}</strong>
          </Typography>
          <Typography variant="body1" sx={{ mb: 2 }}>
            Uploaded at: <strong>{lastUpload.timestamp}</strong>
          </Typography>
        </>
      ) : (
        <Typography variant="body1" sx={{ mb: 2 }}>
          Upload data to see visualizations.
        </Typography>
      )}

      <canvas ref={chartRef} style={{ maxWidth: "100%", height: "400px" }} />
    </Container>
  );
}
