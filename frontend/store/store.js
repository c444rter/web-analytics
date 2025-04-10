// store/store.js
import { configureStore, createSlice } from "@reduxjs/toolkit";

// Set up initial state for your app; here we store basic user info and details about the last upload.
const initialState = {
  user: null,
  lastUpload: null,
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
  },
});

export const { setUser, setLastUpload } = appSlice.actions;

export const store = configureStore({
  reducer: {
    app: appSlice.reducer,
  },
});
