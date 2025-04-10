// components/KpiLineChart.jsx

import React from "react";
import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis,
  CartesianGrid, Tooltip, Legend
} from "recharts";

/**
 * Props:
 * - data: array of objects with { date, orderCount }
 *   or possibly { hour_block, count_orders }
 * - xKey: string (defaults to "date")
 * - yKey: string (defaults to "orderCount")
 * - color: string - CSS color for the line (default "#FFD700" for yellow/gold)
 */
export default function KpiLineChart({
  data,
  xKey = "date",
  yKey = "orderCount",
  color = "#FFD700",
}) {
  // Example: data = [ { date: '2025-01-06', orderCount: 496 }, ... ]
  // Recharts needs numeric or string x-values. 
  // If date is a string, it will show them as text labels along the X-axis.

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey={xKey} />
        <YAxis />
        <Tooltip />
        <Legend />
        <Line 
          type="monotone" 
          dataKey={yKey} 
          stroke={color} 
          strokeWidth={2}
          dot={false}
          activeDot={{ r: 6 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
