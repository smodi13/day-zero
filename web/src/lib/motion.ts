"use client";

import { useEffect, useRef, useState } from "react";

/**
 * Dependency-free motion primitives.
 *
 * Everything this site needs — scroll reveal, staged diagram activation, chart
 * value tweens, pointer parallax — is expressible with IntersectionObserver,
 * requestAnimationFrame and CSS transforms. A general animation framework would
 * add tens of kilobytes to a static research site whose whole argument is that
 * it is fast and inspectable, so these few hooks stand in for one.
 *
 * Two invariants hold across every hook:
 *   1. prefers-reduced-motion jumps straight to the final state — no animation,
 *      no delay, and no loss of information.
 *   2. The final value is what the server renders. Animation is an enhancement
 *      layered on top of correct static output, never the thing that produces it.
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
 * Four safeguards, each covering a real failure mode:
 *   1. threshold 0 — a fractional threshold is unreachable for any block taller
 *      than the viewport, which would leave long sections permanently untriggered.
 *   2. a scroll-position fallback — a fast flick or a programmatic jump can move
 *      further in one frame than the observer samples.
 *   3. `bottom <= 0` — content the reader arrived *below* (anchor link, restored
 *      scroll position) never fires isIntersecting, and must not stay mid-transition.
 *   4. an on-mount check, so anything already on screen reveals immediately.
 */
export function useInView<T extends HTMLElement>(
  { rootMargin = "0px 0px -12% 0px", threshold = 0 } = {},
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
      window.removeEventListener("resize", onScroll);
      io?.disconnect();
    };
    const reveal = () => {
      if (done) return;
      done = true;
      setInView(true);
      cleanup();
    };
    /* Anything at or above the fold has been reached — including content the
       reader arrived *below* via an anchor, a restored scroll position or a
       jump to the end of the page, where `top` is negative. */
    const reached = () => el.getBoundingClientRect().top < window.innerHeight;

    // Synchronous, before any observer exists: a page that mounts already
    // scrolled must not wait for an event that will never come. (This check
    // deliberately does NOT go through requestAnimationFrame — a scheduled
    // callback that re-enters the rAF-coalescing guard below would see its own
    // pending handle and return without ever testing the position.)
    if (reached()) { setInView(true); return; }

    const onScroll = () => {
      if (raf || done) return;
      raf = requestAnimationFrame(() => {
        raf = 0;                      // cleared BEFORE the test, so the guard
        if (reached()) reveal();      // never blocks the check it protects
      });
    };

    let io: IntersectionObserver | null = null;
    if (typeof IntersectionObserver === "undefined") {
      window.addEventListener("scroll", onScroll, { passive: true });
      window.addEventListener("resize", onScroll);
      return cleanup;
    }
    io = new IntersectionObserver((entries) => {
      for (const e of entries) {
        if (e.isIntersecting || e.boundingClientRect.bottom <= 0) reveal();
      }
    }, { rootMargin, threshold });
    io.observe(el);
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);
    return cleanup;
  }, [rootMargin, threshold]);

  return [ref, inView];
}

/**
 * Runs a staged sequence once the element is in view: returns the index of the
 * last stage reached. Under reduced motion every stage is active immediately,
 * so a diagram that uses this to build itself up renders complete instead.
 */
export function useSequence<T extends HTMLElement>(
  stages: number, stepMs = 420,
): [React.RefObject<T | null>, number] {
  const reduced = usePrefersReducedMotion();
  const [ref, inView] = useInView<T>();
  const [step, setStep] = useState(-1);

  useEffect(() => {
    if (reduced) { setStep(stages - 1); return; }
    if (!inView) return;
    let i = 0;
    setStep(0);
    const id = setInterval(() => {
      i += 1;
      setStep(i);
      if (i >= stages - 1) clearInterval(id);
    }, stepMs);
    return () => clearInterval(id);
  }, [inView, reduced, stages, stepMs]);

  return [ref, reduced ? stages - 1 : step];
}

/**
 * "Draw when scrolled to" for bars and rails — with the FINAL state as the
 * base, not the empty one.
 *
 * The obvious implementation (`width: inView ? full : 0`) renders 0 on the
 * server, so with JavaScript disabled every bar on the site is permanently
 * empty. This inverts that: the first render — server and client — is the
 * finished bar. Only after mount, and only when motion is allowed and the
 * element is still below the fold, does it "arm" back to zero so it can grow.
 * A reader who never runs JS, or who prefers reduced motion, simply sees the
 * completed measurement.
 */
export function useDrawOnScroll<T extends HTMLElement>(): [
  React.RefObject<T | null>, boolean,
] {
  const reduced = usePrefersReducedMotion();
  const [ref, inView] = useInView<T>();
  const [armed, setArmed] = useState(false);

  useEffect(() => {
    if (reduced) return;
    const el = ref.current;
    if (!el) return;
    // Only arm content the reader has not reached yet; anything already on
    // screen keeps its real value rather than collapsing to animate.
    if (el.getBoundingClientRect().top > window.innerHeight) setArmed(true);
  }, [ref, reduced]);

  return [ref, reduced || !armed || inView];
}

const easeOutCubic = (t: number) => 1 - Math.pow(1 - t, 3);

/**
 * Tweens a number toward `target` — for chart values that change when the
 * reader switches a control. The first render returns the target exactly, so
 * server output and the pre-interaction state are always the true value.
 */
export function useTweenedNumber(target: number, duration = 620): number {
  const reduced = usePrefersReducedMotion();
  const [value, setValue] = useState(target);
  const fromRef = useRef(target);
  const rafRef = useRef<number | null>(null);

  useEffect(() => {
    if (reduced || duration <= 0) { fromRef.current = target; return; }
    const from = fromRef.current;
    if (from === target) return;
    const start = performance.now();
    const step = (now: number) => {
      const t = Math.min(1, (now - start) / duration);
      setValue(from + (target - from) * easeOutCubic(t));
      if (t < 1) {
        rafRef.current = requestAnimationFrame(step);
      } else {
        fromRef.current = target;
        setValue(target);
      }
    };
    rafRef.current = requestAnimationFrame(step);
    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
      fromRef.current = target;
    };
  }, [target, duration, reduced]);

  return reduced || duration <= 0 ? target : value;
}

/**
 * Pointer offset in the range [-1, 1] for a container, for very subtle depth
 * parallax. Returns [0, 0] on touch devices and under reduced motion, and the
 * listener is never attached in those cases.
 */
export function usePointerOffset<T extends HTMLElement>(): [
  React.RefObject<T | null>, { x: number; y: number },
] {
  const reduced = usePrefersReducedMotion();
  const touch = useIsTouch();
  const ref = useRef<T | null>(null);
  const [off, setOff] = useState({ x: 0, y: 0 });

  useEffect(() => {
    if (reduced || touch) { setOff({ x: 0, y: 0 }); return; }
    const el = ref.current;
    if (!el) return;
    let raf = 0;
    const onMove = (e: PointerEvent) => {
      if (raf) return;
      raf = requestAnimationFrame(() => {
        raf = 0;
        const r = el.getBoundingClientRect();
        if (!r.width || !r.height) return;
        setOff({
          x: Math.max(-1, Math.min(1, ((e.clientX - r.left) / r.width - 0.5) * 2)),
          y: Math.max(-1, Math.min(1, ((e.clientY - r.top) / r.height - 0.5) * 2)),
        });
      });
    };
    const onLeave = () => setOff({ x: 0, y: 0 });
    el.addEventListener("pointermove", onMove);
    el.addEventListener("pointerleave", onLeave);
    return () => {
      if (raf) cancelAnimationFrame(raf);
      el.removeEventListener("pointermove", onMove);
      el.removeEventListener("pointerleave", onLeave);
    };
  }, [reduced, touch]);

  return [ref, off];
}
