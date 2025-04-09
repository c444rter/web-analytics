// components/KpiCard.jsx

import React from "react";
import { Card, CardContent, Typography } from "@mui/material";

/**
 * A simple card that displays a numeric KPI.
 * 
 * Props:
 * - title (string) - Title of the KPI (e.g. "Total Orders")
 * - value (string|number) - The numeric or textual value to show
 * - subtext (string) - Optional subtext or description
 */
export default function KpiCard({ title, value, subtext }) {
  return (
    <Card
      variant="outlined"
      sx={{
        borderRadius: 2,
        minWidth: 200,
        m: 1, // small margin
      }}
    >
      <CardContent>
        <Typography variant="subtitle2" color="textSecondary">
          {title}
        </Typography>
        <Typography variant="h5" fontWeight="bold">
          {value}
        </Typography>
        {subtext && (
          <Typography variant="body2" color="textSecondary">
            {subtext}
          </Typography>
        )}
      </CardContent>
    </Card>
  );
}
