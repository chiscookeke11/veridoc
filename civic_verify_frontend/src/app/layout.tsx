import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import localFont from "next/font/local"

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const uncut_sans = localFont({
  src: [
    {
      path: "../../public/fonts/Uncut-Sans-Regular.otf",
      weight: "400",
      style: "normal",
    }
  ],
  variable: "--font-uncut",
})


const season_vf = localFont({
  src: [
    {
      path: "../../public/fonts/SeasonMix-TRIAL-Regular.otf",
      weight: "400",
      style: "normal",
    }
  ],
  variable: "--font-season-vf",
})


const modern_era_mono = localFont({
  src: [
    {
      path: "../../public/fonts/modern-era-mono-regular.ttf",
      weight: "400",
      style: "normal",
    }
  ],
  variable: "--font-modern_era_mono",
})

export const metadata: Metadata = {
  title: "Civic Verify AI",
  description: "Offline Document Verification and Workflow Agent for Offices",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable}
         ${geistMono.variable}
          ${uncut_sans.variable}
          ${modern_era_mono.variable}
          ${season_vf.variable}
          ${modern_era_mono.variable}
          antialiased`}
      >
        <Navbar />
        {children}
        <Footer />
      </body>
    </html>
  );
}
