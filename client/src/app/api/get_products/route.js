import { cookies } from "next/headers";
import { API_BASE_URL, API_ENDPOINTS } from "@/apiConfig";
import axios from "axios";

export async function GET(req) {
  try {
    const cookieStore = await cookies();
    const token = cookieStore.get("access_token")?.value;

    if (!token) {
      return new Response(
        JSON.stringify({ error: "Unauthorized: Missing credentials" }),
        { status: 401, headers: { "Content-Type": "application/json" } }
      );
    }

    const response = await axios.get(
      `${API_BASE_URL}${API_ENDPOINTS.GET_PRODUCTS}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
          Accept: "application/json",
        },
      }
    );
console.log("Response:", response.data);

    return new Response(JSON.stringify(response.data), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  } catch (error) {
    console.error("Error fetching profile:", error.message);
    return new Response(JSON.stringify({ error: "Internal Server Error" }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }
}