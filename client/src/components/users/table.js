export default function UsersTable({ users = [] }) {
  return (
    <div className="overflow-x-auto mt-8 max-w-4xl mx-2 md:mx-auto  rounded shadow">
      <table className=" min-w-full bg-white border border-gray-200 rounded shadow">
        <thead className="bg-[#C69950] text-white">
          <tr>
            <th className="text-left px-4 py-2 border">First Name</th>
            <th className="text-left px-4 py-2 border">Last Name</th>
            <th className="text-left px-4 py-2 border">Phone Number</th>
            <th className="text-left px-4 py-2 border">Address</th>
          </tr>
        </thead>
        <tbody className="bg-[#0C1825] text-white">
          {users.length === 0 ? (
            <tr>
              <td colSpan={4} className="text-center px-4 py-4 text-gray-500">
                No users found.
              </td>
            </tr>
          ) : (
            users.map((user, idx) => (
              <tr key={idx} className="border-t text-white">
                <td className="px-4 py-2 border">{user.first_name}</td>
                <td className="px-4 py-2 border">{user.last_name}</td>
                <td className="px-4 py-2 border">{user.phone}</td>
                <td className="px-4 py-2 border">{user.address}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
