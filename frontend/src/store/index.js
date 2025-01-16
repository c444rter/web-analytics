import { configureStore, createSlice } from "@reduxjs/toolkit";

const initialState = {
  user: null,
  lastUpload: null, // { timestamp: <string or Date>, fileName: <string> }
};

const appSlice = createSlice({
  name: "app",
  initialState,
  reducers: {
    setUser(state, action) {
      state.user = action.payload;
    },
    setLastUpload(state, action) {
      state.lastUpload = action.payload; 
      // Example payload structure: { timestamp: '2025-01-16T07:00:00Z', fileName: 'myfile.xlsx' }
    },
  },
});

export const { setUser, setLastUpload } = appSlice.actions;

export const store = configureStore({
  reducer: {
    app: appSlice.reducer,
  },
});
