// app/layout.js
"use client";

import React from "react";
import { createTheme, ThemeProvider } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import Navbar from "../components/Navbar";
import SessionProviderWrapper from "../components/SessionProviderWrapper";
import { Provider as ReduxProvider } from "react-redux";
import { store } from "../store/store";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

// Create a QueryClient instance.
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false
    }
  }
});

// Create a custom theme with a dark background and ivory text.
const theme = createTheme({
  palette: {
    mode: "dark",  // set dark mode
    background: {
      default: "#111111",  // very dark (blackish) background
      paper: "#1e1e1e",    // slightly lighter for cards
    },
    text: {
      primary: "#fdfdfd",  // near white (ivory)
      secondary: "#d4d4d4"
    },
    primary: {
      main: "#fdfdfd"      // Ivory (use as your primary accent if needed)
    },
    secondary: {
      main: "#c0b283"      // A soft bone/ivory tone for secondary elements
    }
  }
});

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <SessionProviderWrapper>
          <ReduxProvider store={store}>
            <QueryClientProvider client={queryClient}>
              <ThemeProvider theme={theme}>
                <CssBaseline />
                <Navbar />
                {children}
              </ThemeProvider>
            </QueryClientProvider>
          </ReduxProvider>
        </SessionProviderWrapper>
      </body>
    </html>
  );
}
