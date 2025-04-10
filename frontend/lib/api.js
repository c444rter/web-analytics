// lib/api.js
import axios from "axios";
import { toast } from "react-toastify"; // optional: for notifications

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000",
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor to catch 401 errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Option A: Redirect to login
      if (typeof window !== "undefined") {
        window.location.href = "/login";
      }
      // Option B: Show a toast message and/or handle accordingly
      // toast.error("Your session has expired. Please log in again.");
    }
    return Promise.reject(error);
  }
);

export default api;
