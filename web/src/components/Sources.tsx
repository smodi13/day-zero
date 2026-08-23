import type { SourceRow } from "@/lib/research";

/**
 * Source references without JavaScript. An inline `[S5]` is an anchor to the
 * source ledger at the bottom of the page; the ledger row lights up via the
 * CSS `:target` selector. Works with keyboard, screen readers and JS disabled.
 */
export function SRef({ id }: { id: string }) {
  return (
    <a href={`#src-${id}`}
       className="mono whitespace-nowrap align-baseline text-faint underline decoration-line underline-offset-2 hover:text-signal"
       aria-label={`Source ${id}`}>
      [{id}]
    </a>
  );
}

export function SourceLedger({ sources, title = "Source ledger" }: {
  sources: SourceRow[]; title?: string;
}) {
  return (
    <div className="panel overflow-hidden">
      <p className="eyebrow border-b border-line px-5 py-3">{title}</p>
      <ul>
        {sources.map((s) => (
          <li key={s.id} id={`src-${s.id}`}
              className="src-row flex flex-col gap-1 border-b border-lineSoft px-5 py-3 last:border-b-0 sm:flex-row sm:gap-4">
            <span className="mono shrink-0 pt-0.5 text-dim sm:w-10">{s.id}</span>
            <div className="min-w-0">
              <p className="break-words text-[13.5px] text-text">{s.source}</p>
              <p className="meta mt-0.5 text-[12.5px]">
                <span className="mono uppercase tracking-wider text-faint">{s.type}</span>
                {" — "}{s.establishes.replaceAll("`", "")}
              </p>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
