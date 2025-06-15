import Link from "next/link";

export default function Navbar() {
  return (
    <nav className="bg-[#0C1825] max-w-4xl text-center mx-auto rounded-xl mt-2 flex justify-center px-6 py-4 shadow-md">
      <ul className="flex space-x-16">
        <li>
          <Link
            href="/"
            className="text-white hover:text-[#C69950] font-semibold"
          >
            Products
          </Link>
        </li>
        <li>
          <Link
            href="/users"
            className="text-white hover:text-[#C69950] font-semibold"
          >
            Users
          </Link>
        </li>
        <li>
          <Link
            href="/sold"
            className="text-white hover:text-[#C69950] font-semibold"
          >
            Sold
          </Link>
        </li>
      </ul>
    </nav>
  );
}
