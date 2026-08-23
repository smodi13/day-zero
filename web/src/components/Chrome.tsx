"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { DISCLAIMER } from "@/lib/research";

const ROUTES = [
  { href: "/current-3/", label: "Current 3" },
  { href: "/diligence/sandlock/", label: "Diligence" },
  { href: "/lab/headroom/", label: "Lab" },
  { href: "/signals/", label: "Signals" },
  { href: "/methodology/", label: "Methodology" },
  { href: "/about/", label: "About" },
];

export function Nav() {
  const pathname = usePathname() ?? "/";
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header
      className={`sticky top-0 z-40 border-b transition-[background-color,border-color,box-shadow] duration-300 ${
        scrolled
          ? "border-paper-line bg-paper/85 shadow-[0_1px_0_rgba(20,23,27,.04)] backdrop-blur-md"
          : "border-transparent bg-paper/60 backdrop-blur-sm"
      }`}
    >
      <div className="mx-auto flex max-w-content flex-wrap items-center gap-x-2 gap-y-1 px-4 py-2.5 sm:px-6">
        <Link href="/" className="group mr-auto flex shrink-0 items-baseline gap-2">
          <svg width="15" height="15" viewBox="0 0 24 24" aria-hidden="true"
               className="translate-y-px text-exec">
            <rect x="3" y="3" width="18" height="18" rx="3" fill="none"
                  stroke="currentColor" strokeWidth="1.6" strokeDasharray="4 3" />
            <circle cx="12" cy="12" r="3.4" fill="currentColor"
                    className="origin-center transition-transform duration-500 group-hover:scale-125" />
          </svg>
          <span className="text-[15px] font-semibold tracking-tight">DAY&nbsp;ZERO</span>
        </Link>
        <nav className="flex items-center gap-0.5 overflow-x-auto" aria-label="Primary">
          {ROUTES.map((r) => {
            const active = pathname.startsWith(r.href.replace(/\/$/, ""));
            return (
              <Link key={r.href} href={r.href} className="nav-link whitespace-nowrap"
                    data-active={active ? "true" : "false"}
                    aria-current={active ? "page" : undefined}>
                {r.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}

export function Footer() {
  return (
    <footer className="mt-24 border-t border-paper-line bg-paper-card">
      <div className="mx-auto max-w-content px-4 py-10 sm:px-6">
        <p className="eyebrow">Independence</p>
        <p className="meta mt-2 max-w-prose">{DISCLAIMER}</p>
        <p className="meta mt-4 max-w-prose">
          Local research build. Not published, not deployed, and no person or company
          named here has been contacted about it.
        </p>
        <div className="mono mt-6 text-ink-faint">
          DAY ZERO · Founder Formation &amp; Technical Diligence Engine
        </div>
      </div>
    </footer>
  );
}

export function Section({ id, eyebrow, title, children, lead, className = "" }: {
  id?: string; eyebrow?: string; title?: string; lead?: string;
  children: React.ReactNode; className?: string;
}) {
  return (
    <section id={id}
             className={`mx-auto max-w-content px-4 py-12 sm:px-6 sm:py-16 ${className}`}>
      {eyebrow ? <p className="eyebrow">{eyebrow}</p> : null}
      {title ? <h2 className="h2 mt-2">{title}</h2> : null}
      {lead ? <p className="body mt-3 max-w-prose">{lead}</p> : null}
      <div className={eyebrow || title || lead ? "mt-7" : ""}>{children}</div>
    </section>
  );
}
