import { useState } from "react";

export default function SoldTable({ soldProducts = [] }) {
  const [dateRange, setDateRange] = useState({ from: "", to: "" });

  // Filter products by date range
  const filteredProducts = soldProducts.filter((p) => {
    if (!dateRange.from && !dateRange.to) return true;
    const productDate = new Date(p.date);
    const fromDate = dateRange.from ? new Date(dateRange.from) : null;
    const toDate = dateRange.to ? new Date(dateRange.to) : null;
    if (fromDate && productDate < fromDate) return false;
    if (toDate && productDate > toDate) return false;
    return true;
  });

  return (
    <div>
      {/* Date Range Filter */}
      <div className="flex gap-4 mb-4">
        <div>
          <label className="block text-sm text-white">From</label>
          <input
            type="date"
            value={dateRange.from}
            onChange={(e) =>
              setDateRange((prev) => ({ ...prev, from: e.target.value }))
            }
            className="border rounded px-2 py-1"
          />
        </div>
        <div>
          <label className="block text-sm text-white">To</label>
          <input
            type="date"
            value={dateRange.to}
            onChange={(e) =>
              setDateRange((prev) => ({ ...prev, to: e.target.value }))
            }
            className="border rounded px-2 py-1"
          />
        </div>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full text-white border border-gray-200 rounded shadow">
          <thead className="bg-[#C69950] text-white">
            <tr>
              <th className="text-left px-4 py-2 border">Product Name</th>
              <th className="text-left px-4 py-2 border">Quantity</th>
              <th className="text-left px-4 py-2 border">Each Price</th>
              <th className="text-left px-4 py-2 border">Date</th>
            </tr>
          </thead>
          <tbody>
            {filteredProducts.length === 0 ? (
              <tr>
                <td colSpan={4} className="text-center px-4 py-4 text-white">
                  No sold products in this range.
                </td>
              </tr>
            ) : (
              filteredProducts.map((p, idx) => (
                <tr key={idx} className="border-t text-white">
                  <td className="px-4 py-2 border">{p.name}</td>
                  <td className="px-4 py-2 border">{p.quantity}</td>
                  <td className="px-4 py-2 border">{p.price}</td>
                  <td className="px-4 py-2 border">{p.date}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
