"use client";
import React, { useState } from "react";
import SoldTable from "../../components/sold/table";

export default function SoldPage() {
  const [form, setForm] = useState({
    name: "",
    quantity: "",
    price: "",
  });

  const [soldProducts, setSoldProducts] = useState([
    // Example data for demonstration
    { name: "Product A", quantity: 2, price: 100, date: "2025-05-17" },
    { name: "Product B", quantity: 1, price: 200, date: "2025-05-18" },
  ]);

  const handleChange = (e) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // You can handle the form submission logic here
    alert(
      `Product: ${form.name}\nQuantity: ${form.quantity}\nPrice: ${form.price}`
    );
    setForm({ name: "", quantity: "", price: "" });
  };

  return (
    <div className="max-w-4xl mx-auto mt-2 p-6 bg-[#0C1825] rounded shadow text-white">
      <h1 className="text-2xl font-bold mb-6 text-white">Sold Products</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="text"
          name="name"
          value={form.name}
          onChange={handleChange}
          placeholder="Product Name"
          className="border rounded px-4 py-2 w-full"
        />
        <input
          type="number"
          name="quantity"
          value={form.quantity}
          onChange={handleChange}
          placeholder="Quantity"
          className="border rounded px-4 py-2 w-full"
        />
        <input
          type="number"
          name="price"
          value={form.price}
          onChange={handleChange}
          placeholder="Price"
          className="border rounded px-4 py-2 w-full"
        />
        <button
          type="submit"
          className="bg-[#C69950] text-white mb-4 font-bold rounded px-4 py-2 w-full hover:bg-[#c6c450]"
        >
          Submit
        </button>
      </form>
      <SoldTable soldProducts={soldProducts} />
    </div>
  );
}
