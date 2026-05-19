import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Applied AI Eval Lab",
  description: "Enterprise document intelligence and AI evaluation workspace"
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

