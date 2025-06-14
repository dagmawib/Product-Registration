"use client";

import { useEffect, useState } from "react";
import useSWRMutation from "swr/mutation";
import useSWR from "swr";

const fetcher = (url) => fetch(url).then((res) => res.json());

export default function UpdateProductModal({ open, onClose, product }) {
  const [form, setForm] = useState(product ?? {});

  useEffect(() => {
    setForm(product ?? {});
  }, [product]);

  const { mutate } = useSWR("/api/get_products", fetcher); // Reuse your existing SWR

  const updateProduct = async (url, { arg }) => {
    const res = await fetch(url, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(arg),
    });

    if (!res.ok) {
      const errorData = await res.json();
      throw new Error(errorData.error || "Failed to update product");
    }

    return res.json();
  };

  const {
    trigger,
    isMutating: isUpdating,
    error,
  } = useSWRMutation("/api/update_product", updateProduct);

  if (!open) return null;

  const handleChange = (e) =>
    setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const payload = {
        id: product.id,
        name: form.name,
        purchase_price: form.purchase_price,
        max_sell_price: form.max_sell_price,
        quantity: form.quantity,
        category: form.category,
        date: form.date,
      };

      await trigger(payload);
      mutate();

      onClose();
    } catch (err) {
      console.error("Update failed:", err.message);
      alert("Update failed: " + err.message);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="w-[90%] max-w-md bg-white dark:bg-[#0C1825] text-black dark:text-white rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Update Product</h3>

        <form onSubmit={handleSubmit} className="space-y-3">
          {[
            ["name", "Product Name"],
            ["purchase_price", "Purchase Price"],
            ["quantity", "Quantity"],
            ["max_sell_price", "Sell Price"],
            ["date", "Date"],
            ["category", "Category"],
          ].map(([key, label]) => (
            <div key={key} className="flex flex-col">
              <label className="text-sm font-medium mb-1">{label}</label>
              <input
                required
                type={key === "date" ? "date" : "text"}
                name={key}
                value={form[key] ?? ""}
                onChange={handleChange}
                className="border rounded px-3 py-2"
              />
            </div>
          ))}

          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded text-white border-2 border-[#C99346] hover:text-[#0F172A] hover:bg-gray-300"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isUpdating}
              className="px-4 py-2 rounded bg-[#C99346] text-[#0F172A] hover:opacity-90"
            >
              {isUpdating ? "Saving..." : "Save"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
