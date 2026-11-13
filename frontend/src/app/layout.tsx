import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Frugal Coder — The Budget-Aware, Privacy-First AI Coding Agent",
  description: "Build smarter. Spend less. Ship securely.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-[#090d16] text-slate-100 antialiased selection:bg-blue-600 selection:text-white">
        {children}
      </body>
    </html>
  );
}

