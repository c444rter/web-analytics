// store/store.js
import { configureStore, createSlice } from "@reduxjs/toolkit";

// Set up initial state for your app; here we store basic user info and details about the last upload.
const initialState = {
  user: null,
  lastUpload: null,
  dashboardSelection: null, // Store the selected upload ID for dashboard
  projectionsSelection: null, // Store the selected upload ID for projections
};

const appSlice = createSlice({
  name: "app",
  initialState,
  reducers: {
    setUser(state, action) {
      state.user = action.payload;
    },
    setLastUpload(state, action) {
      state.lastUpload = action.payload; // Ex: { timestamp: '2025-01-16T07:00:00Z', fileName: 'myfile.xlsx' }
    },
    setDashboardSelection(state, action) {
      state.dashboardSelection = action.payload; // Store the selected upload ID and mode
    },
    setProjectionsSelection(state, action) {
      state.projectionsSelection = action.payload; // Store the selected upload ID and forecast type
    },
  },
});

export const { 
  setUser, 
  setLastUpload, 
  setDashboardSelection, 
  setProjectionsSelection 
} = appSlice.actions;

export const store = configureStore({
  reducer: {
    app: appSlice.reducer,
  },
});
