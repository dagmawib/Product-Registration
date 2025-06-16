"use client";
import { useState } from "react";
import useSWR from "swr";
import ProductTable from "@/components/table";
import { toast, Toaster } from "react-hot-toast";
import { Icon } from "@iconify/react";

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
          className="border-1 border-gray-700 rounded px-4 py-2"
        />
        <input
          type="number"
          name="purchase_price"
          value={form.purchase_price}
          onChange={handleChange}
          placeholder="Purchase Price"
          className="border-1 border-gray-700 rounded px-4 py-2"
        />
        <input
          type="number"
          name="quantity"
          value={form.quantity}
          onChange={handleChange}
          placeholder="Quantity"
          className="border-1 border-gray-700 rounded px-4 py-2"
        />
        <input
          type="number"
          name="max_sell_price"
          value={form.max_sell_price}
          onChange={handleChange}
          placeholder="Max Sell Price"
          className="border-1 border-gray-700 rounded px-4 py-2"
        />
        {/* Category Dropdown moved next to Sell Price */}
        <select
          name="category"
          value={form.category}
          onChange={handleChange}
          className="border-1 border-gray-700 rounded px-4 py-2"
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
          className="border-1 border-gray-700 rounded px-4 py-2"
        />

        <button class="group relative outline-0 bg-sky-200 w-full md:w-1/2 h-12 border border-solid border-transparent rounded-xl flex items-center justify-center cursor-pointer transition-transform duration-200 active:scale-[0.95] bg-[linear-gradient(45deg,#efad21,#ffd60f)] [box-shadow:#3c40434d_0_1px_2px_0,#3c404326_0_2px_6px_2px,#0000004d_0_30px_60px_-30px,#34343459_0_-2px_6px_0_inset]">
          <svg
            class="animate-pulse absolute z-10 overflow-visible transition-all duration-300 text-[#ffea50] group-hover:text-white left-2 top-1/2 -translate-y-1/2 h-5 w-5 group-hover:h-6 group-hover:w-6"
            stroke="none"
            viewBox="0 0 24 24"
            fill="currentColor"
          >
            <path
              fill-rule="evenodd"
              clip-rule="evenodd"
              d="M9 4.5a.75.75 0 01.721.544l.813 2.846a3.75 3.75 0 002.576 2.576l2.846.813a.75.75 0 010 1.442l-2.846.813a3.75 3.75 0 00-2.576 2.576l-.813 2.846a.75.75 0 01-1.442 0l-.813-2.846a3.75 3.75 0 00-2.576-2.576l-2.846-.813a.75.75 0 010-1.442l2.846-.813A3.75 3.75 0 007.466 7.89l.813-2.846A.75.75 0 019 4.5z"
            ></path>
          </svg>

          <span class="text-white font-extrabold leading-none text-base transform transition-all duration-300 pl-8 group-hover:translate-x-2 group-hover:opacity-60">
            Add Product
          </span>
        </button>
      </form>
      <h2 className="text-xl font-bold mb-4 text-white">Product List</h2>
      <ProductTable products={products} />
    </div>
  );
}
