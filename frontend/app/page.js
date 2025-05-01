// app/page.js
"use client";

import React from "react";
import { Box, Typography, Button, Container, Grid, Paper, useTheme } from "@mui/material";
import { useRouter } from "next/navigation";
import DashboardIcon from "@mui/icons-material/Dashboard";
import UploadFileIcon from "@mui/icons-material/UploadFile";
import HistoryIcon from "@mui/icons-material/History";
import ShowChartIcon from "@mui/icons-material/ShowChart";
import { useSession } from "next-auth/react";

export default function HomePage() {
  const router = useRouter();
  const theme = useTheme();
  const { status } = useSession();
  
  const isAuthenticated = status === "authenticated";

  const features = [
    {
      title: "Interactive Dashboards",
      description: "View comprehensive analytics of your Shopify store's performance with customizable KPIs.",
      icon: <DashboardIcon sx={{ fontSize: 40, color: theme.palette.secondary.main }} />,
      path: "/dashboard"
    },
    {
      title: "Data Upload",
      description: "Easily upload your Shopify order data for in-depth analysis and insights.",
      icon: <UploadFileIcon sx={{ fontSize: 40, color: theme.palette.secondary.main }} />,
      path: "/upload"
    },
    {
      title: "Historical Analysis",
      description: "Access and compare your past uploads to track performance over time.",
      icon: <HistoryIcon sx={{ fontSize: 40, color: theme.palette.secondary.main }} />,
      path: "/historical"
    },
    {
      title: "Sales Forecasting",
      description: "Predict future sales trends with our advanced machine learning models.",
      icon: <ShowChartIcon sx={{ fontSize: 40, color: theme.palette.secondary.main }} />,
      path: "/projections"
    }
  ];

  return (
    <Container maxWidth="lg">
      {/* Hero Section */}
      <Box 
        sx={{ 
          textAlign: "center", 
          py: 8,
          borderRadius: 2,
          position: 'relative',
          overflow: 'hidden',
          mb: 6
        }}
      >
        <Typography 
          variant="h2" 
          component="h1" 
          gutterBottom
          sx={{ 
            fontWeight: 'bold',
            background: `linear-gradient(45deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            mb: 3
          }}
        >
          DAVIDS
        </Typography>
        <Typography 
          variant="h5" 
          color="textSecondary" 
          paragraph
          sx={{ maxWidth: 700, mx: 'auto', mb: 4 }}
        >
          Advanced Shopify Analytics for Data-Driven Decisions
        </Typography>
        
        {isAuthenticated ? (
          <Button 
            variant="contained" 
            size="large"
            onClick={() => router.push("/dashboard")}
            sx={{ 
              px: 4, 
              py: 1.5,
              backgroundColor: theme.palette.secondary.main,
              color: '#000',
              '&:hover': {
                backgroundColor: '#e6c200',
              }
            }}
          >
            Go to Dashboard
          </Button>
        ) : (
          <Button 
            variant="contained" 
            size="large"
            onClick={() => router.push("/login")}
            sx={{ 
              px: 4, 
              py: 1.5,
              backgroundColor: theme.palette.secondary.main,
              color: '#000',
              '&:hover': {
                backgroundColor: '#e6c200',
              }
            }}
          >
            Sign In
          </Button>
        )}
      </Box>

      {/* Features Section */}
      <Typography 
        variant="h4" 
        component="h2" 
        align="center" 
        gutterBottom
        sx={{ mb: 4 }}
      >
        Powerful Analytics Features
      </Typography>
      
      <Grid container spacing={4} sx={{ mb: 8 }}>
        {features.map((feature, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Paper 
              elevation={3} 
              sx={{ 
                p: 3, 
                height: '100%', 
                display: 'flex', 
                flexDirection: 'column',
                alignItems: 'center',
                textAlign: 'center',
                transition: 'transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out',
                cursor: 'pointer',
                '&:hover': {
                  transform: 'translateY(-5px)',
                  boxShadow: '0 12px 20px rgba(0, 0, 0, 0.2)',
                }
              }}
              onClick={() => isAuthenticated && router.push(feature.path)}
            >
              <Box sx={{ mb: 2 }}>
                {feature.icon}
              </Box>
              <Typography variant="h6" component="h3" gutterBottom>
                {feature.title}
              </Typography>
              <Typography variant="body2" color="textSecondary" sx={{ flexGrow: 1 }}>
                {feature.description}
              </Typography>
            </Paper>
          </Grid>
        ))}
      </Grid>

      {/* Call to Action */}
      {!isAuthenticated && (
        <Paper 
          elevation={3} 
          sx={{ 
            p: 4, 
            textAlign: 'center',
            background: 'linear-gradient(to right, #1e1e1e, #2d2d2d)',
            mb: 6
          }}
        >
          <Typography variant="h5" gutterBottom>
            Ready to optimize your Shopify store?
          </Typography>
          <Typography variant="body1" paragraph sx={{ maxWidth: 700, mx: 'auto', mb: 3 }}>
            Sign in to access all features and start analyzing your Shopify order data today.
          </Typography>
          <Button 
            variant="outlined" 
            size="large"
            onClick={() => router.push("/login")}
            sx={{ 
              borderColor: theme.palette.secondary.main,
              color: theme.palette.secondary.main,
              '&:hover': {
                borderColor: '#e6c200',
                backgroundColor: 'rgba(255, 215, 0, 0.1)',
              }
            }}
          >
            Get Started
          </Button>
        </Paper>
      )}
    </Container>
  );
}
