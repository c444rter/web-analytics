// app/layout.js
"use client"; // So we can use MUI, NextAuth, Redux, etc.

import React from "react";
import { createTheme, ThemeProvider } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import Navbar from "./components/Navbar";
import SessionProviderWrapper from "./components/SessionProviderWrapper";

// IMPORTS FOR REDUX
import { Provider as ReduxProvider } from "react-redux";
import { store } from "../store";

const theme = createTheme({
  palette: {
    mode: "light",
    primary: { main: "#1976d2" },
  },
});

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        {/* WRAP in NextAuth session provider */}
        <SessionProviderWrapper>
          {/* WRAP in Redux provider so all pages can useDispatch() / useSelector() */}
          <ReduxProvider store={store}>
            <ThemeProvider theme={theme}>
              <CssBaseline />
              <Navbar />
              {children}
            </ThemeProvider>
          </ReduxProvider>
        </SessionProviderWrapper>
      </body>
    </html>
  );
}
