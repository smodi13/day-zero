"use client";

import { useEffect, useRef, useState } from "react";

/**
 * Dependency-free motion primitives.
 *
 * Every hook honours prefers-reduced-motion by jumping to the final state, and
 * every animated element is readable in its BASE state — the reveal only ever
 * removes a translate, never an opacity. Content can never be stranded invisible.
 */

export function usePrefersReducedMotion(): boolean {
  const [reduced, setReduced] = useState(false);
  useEffect(() => {
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    const apply = () => setReduced(mq.matches);
    apply();
    mq.addEventListener("change", apply);
    return () => mq.removeEventListener("change", apply);
  }, []);
  return reduced;
}

export function useIsTouch(): boolean {
  const [touch, setTouch] = useState(false);
  useEffect(() => {
    const mq = window.matchMedia("(hover: none), (pointer: coarse)");
    const apply = () => setTouch(mq.matches);
    apply();
    mq.addEventListener("change", apply);
    return () => mq.removeEventListener("change", apply);
  }, []);
  return touch;
}

/**
 * Fires once when the element first reaches the viewport, then disconnects.
 *
 * Three safeguards, each covering a real failure mode:
 *   1. threshold 0 — a fractional threshold is unreachable for any block taller
 *      than the viewport, which would leave long sections permanently untriggered.
 *   2. a scroll-position fallback — a fast flick or a programmatic jump can move
 *      further in one frame than the observer samples.
 *   3. `bottom <= 0` — content the reader arrived *below* (anchor link, restored
 *      scroll position) never fires isIntersecting, and must not stay mid-transition.
 */
export function useInView<T extends HTMLElement>(
  { rootMargin = "0px 0px -10% 0px", threshold = 0 } = {},
): [React.RefObject<T | null>, boolean] {
  const ref = useRef<T | null>(null);
  const [inView, setInView] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    let raf = 0;
    let done = false;

    const cleanup = () => {
      if (raf) cancelAnimationFrame(raf);
      window.removeEventListener("scroll", onScroll);
      io?.disconnect();
    };
    const reveal = () => {
      if (done) return;
      done = true;
      setInView(true);
      cleanup();
    };
    const onScroll = () => {
      if (raf || done) return;
      raf = requestAnimationFrame(() => {
        raf = 0;
        if (el.getBoundingClientRect().top < window.innerHeight) reveal();
      });
    };

    let io: IntersectionObserver | null = null;
    if (typeof IntersectionObserver === "undefined") {
      raf = requestAnimationFrame(reveal);
      return cleanup;
    }
    io = new IntersectionObserver((entries) => {
      for (const e of entries) {
        if (e.isIntersecting || e.boundingClientRect.bottom <= 0) reveal();
      }
    }, { rootMargin, threshold });
    io.observe(el);
    window.addEventListener("scroll", onScroll, { passive: true });
    // Catch anything already on screen at mount (direct route load, restored scroll).
    raf = requestAnimationFrame(onScroll);
    return cleanup;
  }, [rootMargin, threshold]);

  return [ref, inView];
}
