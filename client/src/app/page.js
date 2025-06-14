"use client";
<<<<<<< HEAD

import { useState } from "react";
import { setCookie } from "cookies-next";
import { useRouter } from "next/navigation";
import withAuth from "@/withAuth";

function Home() {
  const [form, setForm] = useState({ username: "", password: "" });
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const router = useRouter();
=======
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
    sell_price: "",
    date: "",
    category: "",
  });
>>>>>>> bfe956ed8a672f2c4e9d7dcf69518bb3b353fe69

  const { data: products = [], mutate } = useSWR("/api/get_products", fetcher);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

<<<<<<< HEAD
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(form),
      });

      if (!res.ok) {
        setLoading(false);
        const errorData = await res.json();
        let backendMsg =
          errorData?.error ||
          errorData?.details?.message ||
          "Login failed. Please check your credentials.";
        toast.error(backendMsg, {
          position: "top-right",
          autoClose: 5000,
          hideProgressBar: false,
          closeOnClick: true,
          pauseOnHover: true,
          draggable: true,
        });
        return;
      }

      const responseData = await res.json();
      if (responseData) {
        setMessage("Login successful!");
        setCookie("access_token", responseData.access_token);
        router.push("/dashboard");
      }
    } catch (err) {
      setError(err.message);
=======
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
      !form.sell_price ||
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
        sell_price: "",
        date: "",
        category: "",
      });
      toast.success("Product added successfully!");
    } else {
      toast.error("Failed to add product. Please try again.");
>>>>>>> bfe956ed8a672f2c4e9d7dcf69518bb3b353fe69
    }
  };

  return (
<<<<<<< HEAD
    <div className="min-h-screen flex items-center justify-center px-4 md:px-0">
      <div className="w-full max-w-md p-8 bg-white dark:bg-[#0C1825] rounded-2xl shadow-lg">
        <h2 className="text-2xl font-bold text-center mb-6 text-[#0F172A] dark:text-white">
          Login
        </h2>

        {error && (
          <p className="text-red-500 text-sm mb-4 text-center">{error}</p>
        )}
        {message && (
          <p className="text-green-500 text-sm mb-4 text-center">{message}</p>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1 text-[#0F172A] dark:text-white">
              Email
            </label>
            <input
              type="email"
              name="username"
              value={form.username}
              onChange={handleChange}
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#C99346] dark:bg-gray-800 dark:text-white"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1 text-[#0F172A] dark:text-white">
              Password
            </label>
            <input
              type="password"
              name="password"
              value={form.password}
              onChange={handleChange}
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#C99346] dark:bg-gray-800 dark:text-white"
            />
          </div>

          <button
            type="submit"
            className="w-full bg-[#C99346] text-white font-semibold py-2 rounded-lg hover:opacity-90 transition"
          >
            Login
          </button>
        </form>

        {/* <p className="mt-4 text-sm text-center text-[#0F172A] dark:text-white">
          Don’t have an account? <a href="/register" className="text-[#C99346] underline">Sign up</a>
        </p> */}
      </div>
=======
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
          name="sell_price"
          value={form.sell_price}
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
      <ProductTable products={products} />
>>>>>>> bfe956ed8a672f2c4e9d7dcf69518bb3b353fe69
    </div>
  );
}

export default withAuth(Home);