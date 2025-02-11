"use client";

import { configureStore } from "@reduxjs/toolkit";
import someReducer from "./features/someSlice";

export const store = configureStore({
  reducer: {
    some: someReducer,
  },
});
