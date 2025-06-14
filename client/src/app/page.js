"use client";
import { useState } from "react";
import useSWR from "swr";
import ProductTable from "../components/table";
import { toast, Toaster } from "react-hot-toast";

const fetcher = (url) => fetch(url).then((res) => res.json());

export default function Page() {
  const [form, setForm] = useState({
    name: "",
    purchase_price: "",
    quantity: "",
    max_sell_price: "",
    date: "",
    category: "",
  });

  const { data: products = [], mutate } = useSWR("/api/get_products", fetcher);

  const handleChange = (e) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  // Function to send product data to the API
  const sendProductToApi = async (productData) => {
    try {
      const response = await fetch("/api/add_product", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(productData),
      });
      if (!response.ok) {
        throw new Error("Failed to add product");
      }
      return await response.json();
    } catch (error) {
      console.error(error);
      return null;
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (
      !form.name ||
      !form.purchase_price ||
      !form.quantity ||
      !form.max_sell_price ||
      !form.date ||
      !form.category
    ) {
      toast.error("Please fill in all fields.");
      return;
    }

    // Send to API
    const result = await sendProductToApi(form);
    if (result) {
      mutate(); // revalidate products list
      setForm({
        name: "",
        purchase_price: "",
        quantity: "",
        max_sell_price: "",
        date: "",
        category: "",
      });
      toast.success("Product added successfully!");
    } else {
      toast.error("Failed to add product. Please try again.");
    }
  };

  return (
    <div className="max-w-4xl md:mx-auto px-4 mx-2 py-8 bg-[#0C1825] shadow-md rounded mt-2">
      <Toaster position="top-right" />
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
          name="purchase_price"
          value={form.purchase_price}
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
          name="max_sell_price"
          value={form.max_sell_price}
          onChange={handleChange}
          placeholder="Max Sell Price"
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
      <ProductTable products={products} />
    </div>
  );
}
