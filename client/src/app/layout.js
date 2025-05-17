import "./globals.css";
import Navbar from "@/components/common/Navbar";

export const metadata = {
  title: "Suk",
  description: "Where merchat register their products",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="bg-white">
        <Navbar />
        {children}
      </body>
    </html>
  );
}
