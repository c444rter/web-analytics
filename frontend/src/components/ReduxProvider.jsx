"use client";
// ^ We must use "use client" because we'll use React hooks (redux) in this component

import React from "react";
import { Provider } from "react-redux";
import { store } from "../store";

export default function ReduxProvider({ children }) {
  return <Provider store={store}>{children}</Provider>;
}
