"use client";

import type { ReactNode } from "react";
import { useInView } from "@/lib/motion";

/**
 * Transform-only reveal. The child is ALWAYS opaque — if this component never
 * mounts, never observes, or freezes, the content still reads. Only a 10px
 * translate is animated.
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
