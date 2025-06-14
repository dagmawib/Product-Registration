"use client";
import { useEffect, useState } from "react";

export default function UpdateProductModal({ open, onClose, product, onSave }) {
  const [form, setForm] = useState(product ?? {});

  
  useEffect(() => setForm(product ?? {}), [product]);

  if (!open) return null; 

  const handleChange = (e) =>
    setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(form);           
    onClose();              
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="w-[90%] max-w-md bg-white dark:bg-[#0C1825] text-black dark:text-white rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Update Product</h3>

        <form onSubmit={handleSubmit} className="space-y-3">
          {[
            ["name", "Product Name"],
            ["purchasePrice", "Purchase Price"],
            ["quantity", "Quantity"],
            ["sellPrice", "Sell Price"],
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
              className="px-4 py-2 rounded bg-[#C99346] text-[#0F172A] hover:opacity-90"
            >
              Save
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
