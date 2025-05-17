"use client";
import { useState } from "react";
import ProductTable from "../components/table";

export default function Page() {
  const [products, setProducts] = useState([]);
  const [form, setForm] = useState({
    name: "",
    purchasePrice: "",
    quantity: "",
    sellPrice: "",
    date: "",
  });

  const handleChange = (e) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (
      !form.name ||
      !form.purchasePrice ||
      !form.quantity ||
      !form.sellPrice ||
      !form.date
    )
      return;

    setProducts((prev) => [...prev, form]);
    setForm({
      name: "",
      purchasePrice: "",
      quantity: "",
      sellPrice: "",
      date: "",
    });
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 bg-[#0C1825] shadow-md rounded mt-2">
      <h1 className="text-2xl font-bold mb-6 text-white">Add Product</h1>

      <form
        onSubmit={handleSubmit}
        className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8 text-white"
      >
        <input
          type="text"
          name="name"
          value={form.name}
          onChange={handleChange}
          placeholder="Product Name"
          className="border rounded px-4 py-2"
        />
        <input
          type="number"
          name="purchasePrice"
          value={form.purchasePrice}
          onChange={handleChange}
          placeholder="Purchase Price"
          className="border rounded px-4 py-2"
        />
        <input
          type="number"
          name="quantity"
          value={form.quantity}
          onChange={handleChange}
          placeholder="Quantity"
          className="border rounded px-4 py-2"
        />
        <input
          type="number"
          name="sellPrice"
          value={form.sellPrice}
          onChange={handleChange}
          placeholder="Sell Price"
          className="border rounded px-4 py-2"
        />
        <input
          type="date"
          name="date"
          value={form.date}
          onChange={handleChange}
          className="border rounded px-4 py-2 md:col-span-2"
        />
        <button
          type="submit"
          className="bg-[#C69950] text-[#0C1825] rounded px-4 py-2 hover:bg-[#c6c450] md:col-span-2"
        >
          Add Product
        </button>
      </form>
      <h2 className="text-xl font-bold mb-4 text-white">Product List</h2>
      <ProductTable products={products} />
    </div>
  );
}
