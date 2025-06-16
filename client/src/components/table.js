"use client";
import { useState, useMemo } from "react";
import UpdateProductModal from "./UpdateProductModal";

export default function ProductTable({ products, setProducts }) {
  const [search, setSearch] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);

  // Get unique categories from products
  const categories = useMemo(() => {
    const set = new Set(products.map((p) => p.category).filter(Boolean));
    return Array.from(set);
  }, [products]);

  // Filtered products
  const filteredProducts = useMemo(() => {
    return products.filter((p) => {
      const matchesSearch =
        p.name.toLowerCase().includes(search.toLowerCase()) ||
        p.category?.toLowerCase().includes(search.toLowerCase());
      const matchesCategory = categoryFilter
        ? p.category === categoryFilter
        : true;
      return matchesSearch && matchesCategory;
    });
  }, [products, search, categoryFilter]);

  const openModal = (product) => {
    setEditingProduct(product);
    setModalOpen(true);
  };

  const handleSave = (updated) => {
    setProducts((prev) =>
      prev.map((p) => (p === editingProduct ? updated : p))
    );
  };

  return (
    <>
      <div>
        {/* Search and Category Filter */}
        <div className="flex flex-col md:flex-row  mb-4 gap-4">
          <input
            type="text"
            placeholder="Search by name or category..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="border-1 border-gray-700 rounded px-4 py-2 w-full md:w-1/3"
          />
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="border-1 border-gray-700 rounded px-4 py-2 w-full md:w-1/4"
          >
            <option value="">All Categories</option>
            {categories.map((cat) => (
              <option key={cat} value={cat} className="text-[#0C1825]">
                {cat}
              </option>
            ))}
          </select>
          <button
            type="button"
            onClick={() => {
              setSearch("");
              setCategoryFilter("");
            }}
            className="rounded px-4 py-1 border-1 border-gray-700 text-white font-semibold hover:bg-[#efad21] w-full md:w-auto"
          >
            Clear
          </button>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full bg-[#0C1825] border-1 border-gray-700 rounded shadow">
            <thead className="bg-[#efad21] text-white">
              <tr>
                <th className="text-left px-4 py-2 border-1 border-gray-700">Name</th>
                <th className="text-left px-4 py-2 border-1 border-gray-700">Purchase Price</th>
                <th className="text-left px-4 py-2 border-1 border-gray-700">Quantity</th>
                <th className="text-left px-4 py-2 border-1 border-gray-700">Sell Price</th>
                <th className="text-left px-4 py-2 border-1 border-gray-700">Date</th>
                <th className="text-left px-4 py-2 border-1 border-gray-700">Category</th>
              </tr>
            </thead>
            <tbody>
              {filteredProducts.length === 0 ? (
                <tr>
                  <td
                    colSpan={6}
                    className="text-center px-4 py-4 text-gray-500"
                  >
                    No products found.
                  </td>
                </tr>
              ) : (
                filteredProducts.map((p, index) => (
                  <tr
                    key={index}
                    className="border-t text-white"
                    onClick={() => openModal(p)}
                  >
                    <td className="px-4 py-2 border-1 border-gray-700">{p.name}</td>
                    <td className="px-4 py-2 border-1 border-gray-700">{p.purchase_price}</td>
                    <td className="px-4 py-2 border-1 border-gray-700">{p.quantity}</td>
                    <td className="px-4 py-2 border-1 border-gray-700">{p.min_sell_price} - {p.max_sell_price}</td>
                    <td className="px-4 py-2 border-1 border-gray-700">{p.date}</td>
                    <td className="px-4 py-2 border-1 border-gray-700">{p.category}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
      {/* Modal */}
      <UpdateProductModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        product={editingProduct}
        onSave={handleSave}
      />
    </>
  );
}
