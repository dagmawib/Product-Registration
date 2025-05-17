export default function ProductTable({ products }) {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full bg-[#0C1825] border border-gray-200 rounded shadow">
        <thead className="bg-[#C69950] text-white">
          <tr>
            <th className="text-left px-4 py-2 border">Name</th>
            <th className="text-left px-4 py-2 border">Purchase Price</th>
            <th className="text-left px-4 py-2 border">Quantity</th>
            <th className="text-left px-4 py-2 border">Sell Price</th>
            <th className="text-left px-4 py-2 border">Date</th>
          </tr>
        </thead>
        <tbody>
          {products.length === 0 ? (
            <tr>
              <td colSpan={5} className="text-center px-4 py-4 text-gray-500">
                No products added yet.
              </td>
            </tr>
          ) : (
            products.map((p, index) => (
              <tr key={index} className="border-t text-white">
                <td className="px-4 py-2 border">{p.name}</td>
                <td className="px-4 py-2 border">{p.purchasePrice}</td>
                <td className="px-4 py-2 border">{p.quantity}</td>
                <td className="px-4 py-2 border">{p.sellPrice}</td>
                <td className="px-4 py-2 border">{p.date}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
