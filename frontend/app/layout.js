// app/layout.js
"use client";

import React from "react";
import { createTheme, ThemeProvider } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import { Box, Container } from "@mui/material";
import Navbar from "../components/NavBar"; // Updated import to match the correct case
import SessionProviderWrapper from "../components/SessionProviderWrapper";
import { Provider as ReduxProvider } from "react-redux";
import { store } from "../store/store";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

// Create a QueryClient instance with improved caching configuration
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      refetchOnReconnect: false,
      retry: 3,
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000), // Exponential backoff
      staleTime: 1000 * 60 * 5, // 5 minutes
      cacheTime: 1000 * 60 * 30, // 30 minutes
      keepPreviousData: true
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
      main: "#FFD700"      // Gold/yellow for highlights and accents
    }
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontWeight: 500,
    },
    h2: {
      fontWeight: 500,
    },
    h3: {
      fontWeight: 500,
    },
    h4: {
      fontWeight: 500,
    },
    h5: {
      fontWeight: 500,
    },
    h6: {
      fontWeight: 500,
    },
  },
  components: {
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#111111',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundColor: '#1e1e1e',
          borderRadius: 8,
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 4,
          textTransform: 'none',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 8,
        },
      },
    },
  },
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
                <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
                  <Navbar />
                  <Box 
                    component="main" 
                    sx={{ 
                      flexGrow: 1, 
                      pt: 2,
                      pb: 4,
                      backgroundColor: theme.palette.background.default 
                    }}
                  >
                    {children}
                  </Box>
                </Box>
              </ThemeProvider>
            </QueryClientProvider>
          </ReduxProvider>
        </SessionProviderWrapper>
      </body>
    </html>
  );
}
