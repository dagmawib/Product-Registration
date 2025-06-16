"use client";
import { useState } from "react";
import { setCookie } from "cookies-next";
import { useRouter } from "next/navigation";
import withAuth from "@/withAuth";
import { toast } from "react-hot-toast";
import CircularProgress from "@mui/material/CircularProgress";

function Home() {
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(form),
      });

      if (!res.ok) {
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
        setLoading(false);
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
      setLoading(false);
    }
  };

  return (
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
              name="email"
              value={form.email}
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
            className="w-full bg-[#efad21] text-white font-semibold py-2 rounded-lg hover:opacity-90 transition flex items-center justify-center"
            disabled={loading}
          >
            {loading ? (
              <>
                <CircularProgress size={22} color="inherit" className="mr-2" />
              </>
            ) : (
              "Login"
            )}
          </button>
        </form>

        {/* <p className="mt-4 text-sm text-center text-[#0F172A] dark:text-white">
          Don’t have an account? <a href="/register" className="text-[#C99346] underline">Sign up</a>
        </p> */}
      </div>
    </div>
  );
}

export default withAuth(Home);
