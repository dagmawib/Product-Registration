<<<<<<< HEAD
import { cookies } from "next/headers";
=======
// import { cookies } from "next/headers";
>>>>>>> bfe956ed8a672f2c4e9d7dcf69518bb3b353fe69
import { API_BASE_URL, API_ENDPOINTS } from "@/apiConfig";
import axios from "axios";

export async function GET(req) {
  try {
<<<<<<< HEAD
    const cookieStore = await cookies();
    const token = cookieStore.get("access_token")?.value;

    console.log("Token:", token);
    

    if (!token) {
      return new Response(
        JSON.stringify({ error: "Unauthorized: Missing credentials" }),
        { status: 401, headers: { "Content-Type": "application/json" } }
      );
    
    }
=======
    // const cookieStore = await cookies();
    // const token = cookieStore.get("access_token")?.value;

    // if (!token) {
    //   return new Response(
    //     JSON.stringify({ error: "Unauthorized: Missing credentials" }),
    //     { status: 401, headers: { "Content-Type": "application/json" } }
    //   );
    // }
>>>>>>> bfe956ed8a672f2c4e9d7dcf69518bb3b353fe69

    const response = await axios.get(
      `${API_BASE_URL}${API_ENDPOINTS.GET_PRODUCTS}`,
      {
        headers: {
<<<<<<< HEAD
          Authorization: `Bearer ${token}`,
=======
          // Authorization: `Bearer ${token}`,
>>>>>>> bfe956ed8a672f2c4e9d7dcf69518bb3b353fe69
          "Content-Type": "application/json",
          Accept: "application/json",
        },
      }
    );

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