import { cookies } from "next/headers";
import { API_BASE_URL, API_ENDPOINTS } from "@/apiConfig";
import axios from "axios";

export async function PATCH(req) {
  try {
    const cookieStore = await cookies();
    const token = cookieStore.get("access_token")?.value;

    if (!token) {
      return new Response(
        JSON.stringify({ error: "Unauthorized: Missing credentials" }),
        { status: 401, headers: { "Content-Type": "application/json" } }
      );
    }

    const body = await req.json();
    const { product_id, ...updateFields } = body;

    if (!product_id) {
      return new Response(JSON.stringify({ error: "Missing product id" }), {
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
      `${API_BASE_URL}${API_ENDPOINTS.UPDATE_PRODUCT}/${product_id}/`,
      payload,
      {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
          Accept: "application/json",
        },
      }
    );
    if (response.status !== 200) {
      return new Response(
        JSON.stringify({ error: "Failed to update product" }),
        { status: response.status, headers: { "Content-Type": "application/json" } }
      );
    }

    return new Response(JSON.stringify(response.data), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  } catch (error) {
    console.error("Error updating product:", error.message);
    return new Response(JSON.stringify({ error: "Internal Server Error" }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }
}
