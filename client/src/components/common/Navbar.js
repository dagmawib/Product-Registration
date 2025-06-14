import Link from "next/link";

export default function Navbar() {
  return (
<<<<<<< HEAD
    <nav className="bg-[#0C1825] max-w-4xl text-center mx-auto rounded-xl mt-2 flex justify-center px-6 py-4 shadow-md">
=======
    <nav className="bg-[#0C1825] max-w-4xl text-center mx-2 md:mx-auto rounded-xl mt-2 flex justify-center px-6 py-4 shadow-md">
>>>>>>> bfe956ed8a672f2c4e9d7dcf69518bb3b353fe69
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
