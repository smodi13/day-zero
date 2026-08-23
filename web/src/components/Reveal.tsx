"use client";

import type { ReactNode } from "react";
import { useInView, usePrefersReducedMotion } from "@/lib/motion";

const EASE = "cubic-bezier(.22,.61,.36,1)";

/**
 * Section-level scroll reveal — applied to content BLOCKS, never to individual
 * paragraphs. A page where every sentence fades in reads as a marketing site.
 *
 * The child is ALWAYS opaque: only a 10px translate is animated. If this
 * component never mounts, never observes, or an animation freezes, the content
 * still reads. That is a deliberate departure from the more common opacity-0
 * base — a frozen opacity keyframe once stranded critical copy invisible in a
 * sibling project, and no amount of scroll-fallback logic fixes that class of
 * bug the way an opaque base state does.
 */
export function Reveal({ children, className = "", delay = 0 }: {
  children: ReactNode; className?: string; delay?: number;
}) {
  const [ref, shown] = useInView<HTMLDivElement>();
  return (
    <div
      ref={ref}
      className={`dz-reveal ${className}`}
      data-shown={shown ? "true" : "false"}
      style={delay ? { transitionDelay: `${delay}ms` } : undefined}
    >
      {children}
    </div>
  );
}

/**
 * Staggers sibling blocks as the container enters view. Children are wrapped in
 * plain divs, so use this on grids rather than on <ul>/<ol> where the wrapper
 * would break list semantics.
 */
export function RevealStagger({ children, step = 70, className = "" }: {
  children: ReactNode[]; step?: number; className?: string;
}) {
  const reduced = usePrefersReducedMotion();
  const [ref, shown] = useInView<HTMLDivElement>();
  const items = children.filter(Boolean);

  return (
    <div ref={ref} className={className}>
      {items.map((child, i) => (
        <div
          key={i}
          style={reduced ? undefined : {
            transform: shown ? "none" : "translateY(12px)",
            transition: `transform 560ms ${EASE} ${i * step}ms`,
          }}
        >
          {child}
        </div>
      ))}
    </div>
  );
}
