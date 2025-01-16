"use client";

import React, { useState } from "react";
import { useDispatch } from "react-redux";
import { setLastUpload } from "../../store/index";
import Button from "@mui/material/Button";

export default function UploadPage() {
  const dispatch = useDispatch();
  const [selectedFile, setSelectedFile] = useState(null);

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const res = await fetch("http://localhost:8000/upload/", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      console.log("Upload response:", data);

      // Dispatch last upload info to Redux
      dispatch(
        setLastUpload({
          timestamp: new Date().toISOString(),
          fileName: selectedFile.name,
        })
      );

      alert(`Uploaded file: ${selectedFile.name}`);
    } catch (err) {
      console.error("Upload error:", err);
      alert("Error uploading file");
    }
  };

  return (
    <main style={{ padding: "2rem" }}>
      <h1>Upload Your Excel File</h1>
      <input type="file" accept=".csv, .xlsx" onChange={handleFileChange} />
      <Button variant="contained" onClick={handleUpload} style={{ marginLeft: "1rem" }}>
        Upload
      </Button>
    </main>
  );
}
