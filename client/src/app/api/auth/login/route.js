import axios from "axios";
import { API_BASE_URL, API_ENDPOINTS } from "@/apiConfig";

export const POST = async (req) => {
  try {
    const body = await req.json();
    const { email, password } = body;

    if (!email || !password) {
      return new Response(
        JSON.stringify({ error: "Email and password are required" }),
        { status: 400 }
      );
    }

    const requestBody = {
      email,
      password,
    };
    console.log("Request body for login:", requestBody);
    
    const response = await axios.post(
      `${API_BASE_URL}${API_ENDPOINTS.LOGIN}`,
      requestBody,
      {
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
      }
    );
    console.log("Login response:", response.data);

  
    return new Response(JSON.stringify(response.data), {
        status: response.status,
      });
  } catch (error) {
    const errorMessage =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      "An unexpected error occurred.";

    console.error("Login failed:", errorMessage);

    return new Response(
      JSON.stringify({
        error: errorMessage,
        details: error.response?.data || "No additional details",
      }),
      { status: error.response?.status || 500 }
    );
  }
};