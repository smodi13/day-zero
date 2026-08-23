import Link from "next/link";
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
  return (
    <header className="sticky top-0 z-40 border-b border-line bg-base/92 backdrop-blur">
      <nav className="mx-auto flex max-w-content flex-wrap items-center gap-x-5 gap-y-1 px-4 py-3 sm:px-6">
        <Link href="/" className="mr-auto flex items-baseline gap-2 font-semibold tracking-tight">
          <span className="text-signal" aria-hidden="true">◆</span>
          <span>DAY&nbsp;ZERO</span>
        </Link>
        {ROUTES.map((r) => (
          <Link key={r.href} href={r.href}
            className="text-[13px] text-dim transition-colors hover:text-text">
            {r.label}
          </Link>
        ))}
      </nav>
    </header>
  );
}

export function Footer() {
  return (
    <footer className="mt-24 border-t border-line">
      <div className="mx-auto max-w-content px-4 py-10 sm:px-6">
        <p className="eyebrow">Independence</p>
        <p className="meta mt-2 max-w-prose">{DISCLAIMER}</p>
        <p className="meta mt-4 max-w-prose">
          Local research build. Not published, not deployed, and no person or company
          named here has been contacted about it.
        </p>
        <div className="mono mt-6 text-faint">
          DAY ZERO · Founder Formation &amp; Technical Diligence Engine
        </div>
      </div>
    </footer>
  );
}

export function Section({ id, eyebrow, title, children, lead }: {
  id?: string; eyebrow?: string; title?: string; lead?: string; children: React.ReactNode;
}) {
  return (
    <section id={id} className="mx-auto max-w-content px-4 py-12 sm:px-6 sm:py-16">
      {eyebrow ? <p className="eyebrow">{eyebrow}</p> : null}
      {title ? <h2 className="h2 mt-2">{title}</h2> : null}
      {lead ? <p className="body mt-3 max-w-prose">{lead}</p> : null}
      <div className={eyebrow || title || lead ? "mt-7" : ""}>{children}</div>
    </section>
  );
}
