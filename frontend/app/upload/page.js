"use client";

import React, { useState } from "react";
import {
  Box,
  Typography,
  Button,
  Snackbar,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  LinearProgress,
  Container,
  Paper,
  Stack
} from "@mui/material";
import { useRouter } from "next/navigation";
import useUpload from "../../hooks/useUpload";
import api from "../../lib/api";
import { useDispatch } from "react-redux";
import { setLastUpload } from "../../store/store";

export default function UploadPage() {
  const dispatch = useDispatch();
  const router = useRouter();

  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadId, setUploadId] = useState(null);
  const [jobStatus, setJobStatus] = useState("");
  const [progress, setProgress] = useState(0);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: "",
    severity: "info"
  });
  const [kpiDialogOpen, setKpiDialogOpen] = useState(false);

  const { mutateAsync, isLoading } = useUpload();

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
  };

  // Poll job progress using the DB upload_id
  const pollJobStatus = (uploadIdToPoll, interval = 3000) => {
    const intervalId = setInterval(async () => {
      try {
        const { data } = await api.get(`/uploads/status/${uploadIdToPoll}`);
        const newStatus = data.status || "unknown";
        const newPercent = data.percent || 0;
        setJobStatus(newStatus);
        setProgress(newPercent);

        if (newStatus === "processing") {
          setSnackbar({
            open: true,
            message: `Processing: ${newPercent}% complete`,
            severity: "info"
          });
        } else if (newStatus === "completed") {
          clearInterval(intervalId);
          setSnackbar({
            open: true,
            message: "Upload processed successfully!",
            severity: "success"
          });
          if (data.upload_id) setUploadId(data.upload_id);
          setTimeout(() => {
            setKpiDialogOpen(true);
          }, 500);
        } else if (newStatus === "failed") {
          clearInterval(intervalId);
          setSnackbar({
            open: true,
            message: "Processing failed.",
            severity: "error"
          });
        } else {
          setSnackbar({
            open: true,
            message: `Status: ${newStatus}. ${newPercent}% complete`,
            severity: "info"
          });
        }
      } catch (err) {
        clearInterval(intervalId);
        setSnackbar({
          open: true,
          message: "Error checking job status.",
          severity: "error"
        });
      }
    }, interval);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    const formData = new FormData();
    formData.append("file", selectedFile);
    formData.append("file_name", selectedFile.name);
    try {
      const data = await mutateAsync(formData);
      dispatch(
        setLastUpload({
          timestamp: new Date().toISOString(),
          fileName: selectedFile.name
        })
      );
      setSnackbar({
        open: true,
        message: "File uploaded! Processing started...",
        severity: "info"
      });
      // Ensure we get a valid DB upload_id from the response
      if (data.upload_id) {
        setUploadId(data.upload_id);
        // Start polling using the DB upload id (not the Redis job id)
        pollJobStatus(data.upload_id);
      } else {
        console.error("upload_id is missing in response:", data);
      }
    } catch (err) {
      console.error("Upload error:", err);
      setSnackbar({
        open: true,
        message: "Error uploading file.",
        severity: "error"
      });
    }
  };

  const handleChooseDefault = () => {
    setKpiDialogOpen(false);
    if (uploadId) {
      router.push(`/dashboard?upload_id=${uploadId}&mode=default`);
    } else {
      router.push("/dashboard");
    }
  };

  const handleChooseCustom = () => {
    setKpiDialogOpen(false);
    if (uploadId) {
      router.push(`/dashboard?upload_id=${uploadId}&mode=custom`);
    } else {
      router.push("/dashboard");
    }
  };

  return (
    <Container maxWidth="sm" sx={{ mt: 4 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h4" textAlign="center" mb={3}>
          Upload Your File
        </Typography>
        <Stack spacing={2} alignItems="center">
          <input type="file" accept=".csv,.xlsx" onChange={handleFileChange} />
          <Button
            variant="contained"
            onClick={handleUpload}
            disabled={isLoading}
            startIcon={isLoading ? <CircularProgress size={20} color="inherit" /> : null}
          >
            {isLoading ? "Uploading..." : "Upload"}
          </Button>
        </Stack>
      </Paper>

      <Snackbar
        anchorOrigin={{ vertical: "top", horizontal: "center" }}
        open={snackbar.open}
        autoHideDuration={null}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert severity={snackbar.severity} sx={{ width: "100%" }} icon={false}>
          <Box>
            <Typography variant="body2">{snackbar.message}</Typography>
            {jobStatus === "processing" && (
              <Box sx={{ mt: 1 }}>
                <LinearProgress variant="determinate" value={progress} sx={{ height: 8, borderRadius: 1 }} />
                <Typography variant="caption" display="block" textAlign="right">
                  {progress}%
                </Typography>
              </Box>
            )}
          </Box>
        </Alert>
      </Snackbar>

      <Dialog open={kpiDialogOpen} onClose={() => setKpiDialogOpen(false)}>
        <DialogTitle>Select Dashboard Mode</DialogTitle>
        <DialogContent>
          <Typography>
            Your file has been processed. Would you like to view the Default KPI Dashboard (all metrics) or choose custom KPIs?
          </Typography>
        </DialogContent>
        <DialogActions sx={{ justifyContent: "center", p: 2 }}>
          <Button variant="contained" onClick={handleChooseDefault} sx={{ mx: 1 }}>
            Default KPI
          </Button>
          <Button variant="outlined" onClick={handleChooseCustom} sx={{ mx: 1 }}>
            Custom KPI
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}
