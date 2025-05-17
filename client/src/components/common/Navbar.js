import Link from "next/link";

export default function Navbar() {
  return (
    <nav className="bg-gray-100 max-w-4xl text-center mx-auto rounded-2xl mt-2 flex justify-center px-6 py-4 shadow-md">
      <ul className="flex space-x-16">
        <li>
          <Link
            href="/"
            className="text-[#0C1825] hover:text-[#C69950] font-semibold"
          >
            Products
          </Link>
        </li>
        <li>
          <Link
            href="/users"
            className="text-[#0C1825] hover:text-[#C69950] font-semibold"
          >
            Users
          </Link>
        </li>
      </ul>
    </nav>
  );
}
