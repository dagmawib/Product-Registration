
import { API_BASE_URL, API_ENDPOINTS } from "@/apiConfig";
import axios from "axios";

export async function PATCH(req) {
  try {
   

    const body = await req.json();
    const { id, ...updateFields } = body;

    if (!id) {
      return new Response(JSON.stringify({ error: "Missing vehicle_id" }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      });
    }

    const validFields = [
      "name",
      "max_sell_price",
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
      `${API_BASE_URL}${API_ENDPOINTS.UPDATE_PRODUCT}/${id}/`,
      payload,
      {
        headers: {

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
