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
    {
      first_name: " Doe",
      last_name: "John",
      phone: "1234567890",
      address: "123 Main St",
    },
    {
      first_name: " Smith",
      last_name: "Jane",
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
      <div className="max-w-4xl md:mx-auto mt-2 bg-[#0C1825] p-6 mx-2 rounded shadow">
        <h1 className="text-2xl font-bold mb-6 text-white">
          Register Employee
        </h1>
        <form
          onSubmit={handleSubmit}
          className="grid grid-cols-1 md:grid-cols-2 gap-4 text-white"
        >
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
          <div className="col-span-1 md:col-span-2 flex justify-center md:justify-end mt-4">
            <button
              type="submit"
              className="bg-[#C69950] text-white font-bold rounded px-6 py-2 hover:bg-[#c6c450] w-full md:w-auto"
            >
              Register
            </button>
          </div>
        </form>
      </div>

      <UsersTable users={users} />
    </>
  );
}
