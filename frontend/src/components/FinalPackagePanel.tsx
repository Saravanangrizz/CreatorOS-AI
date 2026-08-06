import type { FinalPackage } from "../lib/types";

export function FinalPackagePanel({ pkg }: { pkg: FinalPackage }) {
  return (
    <div className="rounded-xl border border-scope-dim bg-scope/[0.04] p-5 shadow-panel">
      <div className="mb-4 flex items-center gap-2">
        <span className="h-2 w-2 rounded-full bg-scope" />
        <h3 className="font-mono text-[11px] uppercase tracking-[0.14em] text-scope">
          Final package · ready to publish
        </h3>
      </div>

      <h2 className="font-display text-xl font-semibold text-ink">{pkg.recommended_title}</h2>
      <p className="mt-1 text-sm italic text-ink-muted">"{pkg.hook}"</p>
      <p className="mt-3 text-sm text-ink-muted">{pkg.description}</p>

      <div className="mt-4 flex flex-wrap gap-1.5">
        {pkg.tags.map((tag) => (
          <span
            key={tag}
            className="rounded-full border border-base-hairline bg-base-raised px-2 py-0.5 font-mono text-[10px] text-ink-muted"
          >
            {tag}
          </span>
        ))}
        {pkg.hashtags.map((tag) => (
          <span
            key={tag}
            className="rounded-full border border-tally-dim bg-tally/10 px-2 py-0.5 font-mono text-[10px] text-tally"
          >
            {tag}
          </span>
        ))}
      </div>

      <div className="mt-5 grid gap-4 sm:grid-cols-2">
        <div>
          <h4 className="mb-1.5 font-mono text-[11px] uppercase tracking-[0.14em] text-ink-faint">
            Chapters
          </h4>
          <ul className="space-y-1 font-mono text-xs text-ink-muted">
            {pkg.chapters.map((c) => (
              <li key={c.time}>
                <span className="text-ink">{c.time}</span> — {c.label}
              </li>
            ))}
          </ul>
        </div>
        <div>
          <h4 className="mb-1.5 font-mono text-[11px] uppercase tracking-[0.14em] text-ink-faint">
            Publishing checklist
          </h4>
          <ul className="space-y-1 text-sm text-ink-muted">
            {pkg.publishing_checklist.map((c, i) => (
              <li key={i} className="flex gap-2">
                <span className="text-scope">✓</span>
                {c}
              </li>
            ))}
          </ul>
          <p className="mt-2 font-mono text-xs text-ink-faint">
            Best time to publish: <span className="text-ink">{pkg.best_publish_time}</span>
          </p>
        </div>
      </div>

      {pkg.thumbnail_concepts.length > 0 && (
        <div className="mt-5">
          <h4 className="mb-1.5 font-mono text-[11px] uppercase tracking-[0.14em] text-ink-faint">
            Thumbnail concepts
          </h4>
          <div className="grid gap-2 sm:grid-cols-2">
            {pkg.thumbnail_concepts.map((c, i) => (
              <div
                key={i}
                className="rounded-lg border border-base-hairline bg-base-raised p-3 text-sm text-ink-muted"
              >
                <span className="font-medium text-ink">{c.style}:</span> {c.prompt}
              </div>
            ))}
          </div>
        </div>
      )}

      <p className="mt-5 font-mono text-[11px] text-ink-faint">
        Select a stage on the pipeline rail above to see how each agent
        reasoned its way here.
      </p>
    </div>
  );
}
