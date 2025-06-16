"use client";
import { useState } from "react";
import UsersTable from "../../components/users/table";

export default function UsersPage() {
  const [form, setForm] = useState({
    first_name: "",
    last_name: "",
    phone: "",
    address: "",
  });
  const [users, setUsers] = useState([
    // Example data for demonstration
    {
      first_name: "John",
      last_name: "Doe",
      phone: "1234567890",
      address: "123 Main St",
    },
    {
      first_name: "Jane",
      last_name: "Smith",
      phone: "9876543210",
      address: "456 Elm St",
    },
  ]);

  const handleChange = (e) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setUsers((prev) => [...prev, form]);
    setForm({ first_name: "", last_name: "", phone: "", address: "" });
  };

  return (
    <>
      <div className="max-w-md mx-auto mt-2 bg-[#0C1825] p-6 rounded shadow">
        <h1 className="text-2xl font-bold mb-6 text-white">
          Register Employee
        </h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="text"
            name="first_name"
            value={form.first_name}
            onChange={handleChange}
            placeholder="First Name"
            className="border rounded px-4 py-2 w-full"
          />
          <input
            type="text"
            name="last_name"
            value={form.last_name}
            onChange={handleChange}
            placeholder="Last Name"
            className="border rounded px-4 py-2 w-full"
          />
          <input
            type="tel"
            name="phone"
            value={form.phone}
            onChange={handleChange}
            placeholder="Phone Number"
            className="border rounded px-4 py-2 w-full"
          />
          <input
            type="text"
            name="address"
            value={form.address}
            onChange={handleChange}
            placeholder="Address"
            className="border rounded px-4 py-2 w-full"
          />
          <button
            type="submit"
            className="bg-[#C69950] text-white font-bold rounded px-4 py-2 w-full hover:bg-[#c6c450]"
          >
            Register
          </button>
        </form>
      </div>
      <UsersTable users={users} />
    </>
  );
}
