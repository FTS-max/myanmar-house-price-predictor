import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Navbar } from "@/components/layout/navbar";

const geist = Geist({ subsets: ["latin"], variable: "--font-geist-sans" });
const geistMono = Geist_Mono({ subsets: ["latin"], variable: "--font-geist-mono" });

export const metadata: Metadata = {
  title: "Myanmar House Price Predictor",
  description: "Predict house prices in Myanmar with machine learning",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${geist.variable} ${geistMono.variable}`}>
      <body>
        <div className="min-h-screen flex flex-col">
          <Navbar />
          <div className="flex-grow">{children}</div>
          <footer className="bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800 py-6">
            <div className="container mx-auto px-4 text-center text-sm text-gray-600 dark:text-gray-400">
              <p>© {new Date().getFullYear()} Myanmar House Price Predictor. All rights reserved.</p>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
