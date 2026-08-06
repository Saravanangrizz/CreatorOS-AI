import type { ReactNode } from "react";
import type { AgentStepOutput } from "../lib/types";

function renderValue(value: unknown): ReactNode {
  if (Array.isArray(value)) {
    return (
      <ul className="list-inside list-disc space-y-1 text-sm text-ink-muted">
        {value.map((item, i) => (
          <li key={i}>
            {typeof item === "object" && item !== null
              ? Object.values(item as Record<string, unknown>).join(" — ")
              : String(item)}
          </li>
        ))}
      </ul>
    );
  }
  if (typeof value === "object" && value !== null) {
    return (
      <dl className="space-y-1 text-sm text-ink-muted">
        {Object.entries(value as Record<string, unknown>).map(([k, v]) => (
          <div key={k}>
            <dt className="inline font-medium text-ink">{k}: </dt>
            <dd className="inline">{String(v)}</dd>
          </div>
        ))}
      </dl>
    );
  }
  return <p className="text-sm text-ink-muted">{String(value)}</p>;
}

export function StageDetail({ step }: { step: AgentStepOutput }) {
  const { output } = step;
  const { reasoning, ...fields } = output;

  return (
    <div className="rounded-xl border border-base-hairline bg-base-panel p-5 shadow-panel">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="font-display text-lg font-semibold text-ink">{step.display_name}</h3>
        <span className="rounded-full border border-base-hairline bg-base-raised px-2.5 py-1 font-mono text-[10px] uppercase tracking-wide text-ink-faint">
          {step.provider} · {step.model}
        </span>
      </div>

      <div className="space-y-4">
        {Object.entries(fields).map(([key, value]) => (
          <div key={key}>
            <h4 className="mb-1.5 font-mono text-[11px] uppercase tracking-[0.14em] text-ink-faint">
              {key === "suggested_sources" ? "Suggested research sources" : key.replace(/_/g, " ")}
            </h4>
            {key === "suggested_sources" && (
              <p className="mb-1.5 text-xs text-ink-faint">
                No live web search — verify these before citing them as facts.
              </p>
            )}
            {renderValue(value)}
          </div>
        ))}
      </div>

      {typeof reasoning === "string" && reasoning && (
        <div className="mt-5 rounded-lg border border-tally-dim bg-tally/[0.06] p-3">
          <h4 className="mb-1 font-mono text-[10px] uppercase tracking-[0.14em] text-tally">
            Why this recommendation
          </h4>
          <p className="text-sm text-ink-muted">{reasoning}</p>
        </div>
      )}
    </div>
  );
}
