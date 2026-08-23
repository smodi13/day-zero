import type { Metadata } from "next";
import "./globals.css";
import { Footer, Nav } from "@/components/Chrome";

export const metadata: Metadata = {
  title: "DAY ZERO — Founder Formation & Technical Diligence Engine",
  description:
    "An independent research system that surfaces technical builders from public artifacts, " +
    "reproduces their technical claims against real baselines, and reads architecture deeply " +
    "enough to understand the tradeoffs. No founder scores.",
  robots: { index: false, follow: false },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <a href="#main"
           className="sr-only focus:not-sr-only focus:absolute focus:left-3 focus:top-3 focus:z-50 focus:rounded focus:bg-paper focus:px-3 focus:py-2">
          Skip to content
        </a>
        <Nav />
        <main id="main">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
