import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { ClerkProvider } from "@clerk/nextjs";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Berlin AI Chatbot Platform",
  description: "AI chatbot platform for website lead generation and support.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <ClerkProvider>
      <html
        lang="en"
        translate="no"
        suppressHydrationWarning
        className={`${geistSans.variable} ${geistMono.variable} notranslate h-full antialiased`}
      >
        <body
          suppressHydrationWarning
          translate="no"
          className="notranslate min-h-full flex flex-col"
        >
          {children}
        </body>
      </html>
    </ClerkProvider>
  );
}
