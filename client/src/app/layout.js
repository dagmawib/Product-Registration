import "./globals.css";


export const metadata = {
  title: "Suk",
  description: "Where merchat register their products",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="bg-white">
        {children}
      </body>
    </html>
  );
}
