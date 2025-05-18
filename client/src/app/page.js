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
    category: "",
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
      !form.date ||
      !form.category
    )
      return;

    setProducts((prev) => [...prev, form]);
    setForm({
      name: "",
      purchasePrice: "",
      quantity: "",
      sellPrice: "",
      date: "",
      category: "",
    });
  };

  return (
    <div className="max-w-4xl md:mx-auto px-4 mx-2 py-8 bg-[#0C1825] shadow-md rounded mt-2">
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
        {/* Category Dropdown moved next to Sell Price */}
        <select
          name="category"
          value={form.category}
          onChange={handleChange}
          className="border rounded px-4 py-2"
        >
          <option value="">Select Category</option>
          <option value="Electronics" className="text-black">
            Electronics
          </option>
          <option value="Clothing" className="text-black">
            Clothing
          </option>
          <option value="Food" className="text-black">
            Food
          </option>
          <option value="Books" className="text-black">
            Books
          </option>
          <option value="Other" className="text-black">
            Other
          </option>
        </select>
        <input
          type="date"
          name="date"
          value={form.date}
          onChange={handleChange}
          placeholder="Date"
          className="border rounded px-4 py-2"
        />
        <button
          type="submit"
          className="bg-[#C69950] text-white font-bold rounded px-4 py-2 hover:bg-[#c6c450] md:col-span-2"
        >
          Add Product
        </button>
      </form>
      <h2 className="text-xl font-bold mb-4 text-white">Product List</h2>
      <ProductTable products={products} setProducts={setProducts} />
    </div>
  );
}
