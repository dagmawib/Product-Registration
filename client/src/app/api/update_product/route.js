<<<<<<< HEAD

=======
import { cookies } from "next/headers";
>>>>>>> bfe956ed8a672f2c4e9d7dcf69518bb3b353fe69
import { API_BASE_URL, API_ENDPOINTS } from "@/apiConfig";
import axios from "axios";

export async function PATCH(req) {
  try {
<<<<<<< HEAD
   
=======
    const cookieStore = await cookies();
    const token = cookieStore.get("access_token")?.value;

    if (!token) {
      return new Response(
        JSON.stringify({ error: "Unauthorized: Missing credentials" }),
        { status: 401, headers: { "Content-Type": "application/json" } }
      );
    }
>>>>>>> bfe956ed8a672f2c4e9d7dcf69518bb3b353fe69

    const body = await req.json();
    const { id, ...updateFields } = body;

    if (!id) {
      return new Response(JSON.stringify({ error: "Missing vehicle_id" }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      });
    }

    const validFields = [
<<<<<<< HEAD
      "name",
      "max_sell_price",
=======
      "product_name",
      "sell_price",
>>>>>>> bfe956ed8a672f2c4e9d7dcf69518bb3b353fe69
      "purchase_price",
      "quantity",
      "category",
      "date",
    ];

    const payload = {};

    for (const key of validFields) {
      if (updateFields[key] !== undefined) {
        payload[key] = updateFields[key];
      }
    }

    const response = await axios.patch(
<<<<<<< HEAD
      `${API_BASE_URL}${API_ENDPOINTS.UPDATE_PRODUCT}/${id}/`,
      payload,
      {
        headers: {

=======
      `${API_BASE_URL}${API_ENDPOINTS.EDIT_VEHICLE}/${id}/`,
      payload,
      {
        headers: {
          Authorization: `Bearer ${token}`,
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
    console.error("Error updating vehicle:", error.message);
    return new Response(JSON.stringify({ error: "Internal Server Error" }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }
}
