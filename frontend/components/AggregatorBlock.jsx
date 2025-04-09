// components/AggregatorBlock.jsx

import React from "react";
import { Box, Typography } from "@mui/material";
import KpiCard from "./KPICard";
import KpiLineChart from "./KPILineChart";

/**
 * aggregatorKey: one of the 11 keys from your registry
 * aggregatorData: the actual data returned by the backend
 */
export default function AggregatorBlock({ aggregatorKey, aggregatorData }) {
  switch (aggregatorKey) {
    case "orders_summary":
      // aggregatorData = { total_orders, total_revenue, average_order_value }
      return <OrdersSummary aggregatorData={aggregatorData} />;

    case "time_series":
      // aggregatorData = [ { date: "2025-01-06", orderCount: 496 }, ... ]
      return (
        <Box sx={{ my: 2 }}>
          <Typography variant="h6">Daily Orders Over Time</Typography>
          <KpiLineChart
            data={aggregatorData}
            xKey="date"
            yKey="orderCount"
            color="#FFD700" // gold/yellow line
          />
        </Box>
      );

    case "top_cities_by_orders":
      // aggregatorData = [ { city, order_count }, ... ]
      return (
        <SimpleArrayTable
          title="Top Cities by Orders"
          data={aggregatorData}
          columns={["city", "order_count"]}
        />
      );

    case "top_cities_by_revenue":
      // aggregatorData = [ { city, revenue }, ... ]
      return (
        <SimpleArrayTable
          title="Top Cities by Revenue"
          data={aggregatorData}
          columns={["city", "revenue"]}
        />
      );

    case "top_products_by_quantity":
      // aggregatorData = [ { product_name, total_quantity }, ... ]
      return (
        <SimpleArrayTable
          title="Top Products by Quantity"
          data={aggregatorData}
          columns={["product_name", "total_quantity"]}
        />
      );

    case "top_products_by_revenue":
      // aggregatorData = [ { product_name, product_revenue }, ... ]
      return (
        <SimpleArrayTable
          title="Top Products by Revenue"
          data={aggregatorData}
          columns={["product_name", "product_revenue"]}
        />
      );

    case "repeat_customers":
      // aggregatorData = { unique_count, repeat_count, repeat_rate_percent }
      return <RepeatCustomers aggregatorData={aggregatorData} />;

    case "orders_by_hour":
      // aggregatorData = [ { hour_block, count_orders }, ... ]
      return (
        <Box sx={{ my: 2 }}>
          <Typography variant="h6">Hourly Orders</Typography>
          <KpiLineChart
            data={aggregatorData}
            xKey="hour_block"
            yKey="count_orders"
            color="#FFD700"
          />
        </Box>
      );

    case "orders_by_day_of_week":
      // aggregatorData = [ { dow: 0, count_orders: 1571 }, ... ]
      return (
        <SimpleArrayTable
          title="Orders by Day of Week"
          data={aggregatorData}
          columns={["dow", "count_orders"]}
        />
      );

    case "top_discount_codes":
      // aggregatorData = [ { discount_code, code_usage }, ... ]
      return (
        <SimpleArrayTable
          title="Top Discount Codes (Usage)"
          data={aggregatorData}
          columns={["discount_code", "code_usage"]}
        />
      );

    case "top_discount_codes_by_savings":
      // aggregatorData = [ { discount_code, total_discount }, ... ]
      return (
        <SimpleArrayTable
          title="Top Discount Codes (Savings)"
          data={aggregatorData}
          columns={["discount_code", "total_discount"]}
        />
      );

    default:
      // fallback for unknown aggregator keys
      return (
        <Box sx={{ my: 2, p: 2, border: "1px solid #ccc" }}>
          <Typography variant="subtitle2">Aggregator: {aggregatorKey}</Typography>
          <pre>{JSON.stringify(aggregatorData, null, 2)}</pre>
        </Box>
      );
  }
}

/** ------------------------------------------------------------------
 * Sub-Components 
 * ------------------------------------------------------------------*/

/** 
 * For aggregatorKey="orders_summary" 
 * aggregatorData = { total_orders, total_revenue, average_order_value }
 */
function OrdersSummary({ aggregatorData }) {
  return (
    <Box sx={{ my: 2 }}>
      <Typography variant="h6">Orders Summary</Typography>
      <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap" }}>
        <KpiCard title="Total Orders" value={aggregatorData.total_orders} />
        <KpiCard
          title="Total Revenue"
          value={`$${aggregatorData.total_revenue.toFixed(2)}`}
        />
        <KpiCard
          title="Avg Order Value"
          value={`$${aggregatorData.average_order_value.toFixed(2)}`}
        />
      </Box>
    </Box>
  );
}

/**
 * For aggregatorKey="repeat_customers"
 * aggregatorData = { unique_count, repeat_count, repeat_rate_percent }
 */
function RepeatCustomers({ aggregatorData }) {
  return (
    <Box sx={{ my: 2 }}>
      <Typography variant="h6">Repeat Customers</Typography>
      <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap" }}>
        <KpiCard title="Unique Customers" value={aggregatorData.unique_count} />
        <KpiCard title="Repeat Customers" value={aggregatorData.repeat_count} />
        <KpiCard
          title="Repeat Rate (%)"
          value={aggregatorData.repeat_rate_percent.toFixed(2) + "%"}
        />
      </Box>
    </Box>
  );
}

/**
 * A simple array table for aggregator keys returning an array of objects.
 * props:
 * - title (string)
 * - data (array)
 * - columns (string[]) - array of column keys to show
 */
function SimpleArrayTable({ title, data, columns }) {
  return (
    <Box sx={{ my: 2 }}>
      <Typography variant="h6">{title}</Typography>
      <Box
        sx={{
          mt: 1,
          border: "1px solid #ccc",
          borderRadius: 1,
          overflow: "auto",
        }}
      >
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ background: "#f0f0f0" }}>
              {columns.map((col) => {
                // Only change the header text color if the column is "city" or "order_count"
                const lower = col.toLowerCase();
                const headerStyle =
                  lower === "city" || lower === "order_count"
                    ? { color: "black", border: "1px solid #ccc", padding: "6px 8px", textAlign: "left" }
                    : { border: "1px solid #ccc", padding: "6px 8px", textAlign: "left" };
                return (
                  <th key={col} style={headerStyle}>
                    {col}
                  </th>
                );
              })}
            </tr>
          </thead>
          <tbody>
            {data.map((row, idx) => (
              <tr key={idx}>
                {columns.map((col) => (
                  <td
                    key={col}
                    style={{
                      border: "1px solid #ccc",
                      padding: "6px 8px",
                    }}
                  >
                    {row[col]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </Box>
    </Box>
  );
}
