"use client";

import { ThemeProvider, createTheme } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import SessionProviderWrapper from "../components/SessionProviderWrapper";
import ReduxProvider from "../components/ReduxProvider";
import Navbar from "../components/Navbar"; // <-- import your new Navbar
import "../app/globals.css";

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap"
        />
      </head>
      <body>
        <ReduxProvider>
          <SessionProviderWrapper>
            <ThemeProvider
              theme={createTheme({
                typography: { fontFamily: "Roboto, sans-serif" },
                palette: { mode: "light", primary: { main: "#1976d2" } },
              })}
            >
              <CssBaseline />
              <Navbar /> {/* Renders the nav bar on every page */}
              {children}
            </ThemeProvider>
          </SessionProviderWrapper>
        </ReduxProvider>
      </body>
    </html>
  );
}
