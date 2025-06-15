import { getCookie } from "cookies-next";

export const isAuthenticated = () => {
  if (typeof window === "undefined") {
    return false; // Return false during server-side rendering
  }
  const accessToken = getCookie("access_token");

  // Check if the token exists and hasn't expired
  if (accessToken) {
    return true;
  }
  return false;
};
