import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Tilly Repository Builder",
  description: "Build and compile all repositories under Pimonkee profile",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="h-full">{children}</body>
    </html>
  );
}
