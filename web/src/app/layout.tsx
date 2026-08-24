import type { Metadata } from "next";
import "./globals.css";
import { Footer, Nav } from "@/components/Chrome";

/* Set NEXT_PUBLIC_SITE_URL at build time so absolute OG/canonical URLs resolve.
   Falls back to the production alias rather than localhost, since a stale
   localhost URL in a social card is worse than a slightly wrong one. */
const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL ?? "https://day-zero.vercel.app";

/* Indexing is environment-gated rather than hard-coded: preview and local
   builds stay out of search results, production is discoverable. */
const INDEXABLE = process.env.NEXT_PUBLIC_NOINDEX !== "1";

const TITLE = "DAY ZERO | Founder Formation & Technical Diligence Engine";
const DESCRIPTION =
  "A technical venture sourcing and diligence system that moves from public builder " +
  "signals to reproducible claim testing and code-level technical diligence. " +
  "Independent research project — public sources only, no founder scores.";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: { default: TITLE, template: "%s | DAY ZERO" },
  description: DESCRIPTION,
  applicationName: "DAY ZERO",
  authors: [{ name: "Sahil Modi" }],
  alternates: { canonical: "/" },
  robots: INDEXABLE
    ? { index: true, follow: true }
    : { index: false, follow: false },
  openGraph: {
    type: "website",
    siteName: "DAY ZERO",
    title: TITLE,
    description: DESCRIPTION,
    url: "/",
    images: [{ url: "/og.png", width: 1200, height: 630,
               alt: "DAY ZERO — find the builder before the round, test the hard claim before the meeting." }],
  },
  twitter: {
    card: "summary_large_image",
    title: TITLE,
    description: DESCRIPTION,
    images: ["/og.png"],
  },
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
