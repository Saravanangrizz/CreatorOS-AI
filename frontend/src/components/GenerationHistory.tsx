import type { Generation } from "../lib/types";

interface GenerationHistoryProps {
  generations: Generation[];
  activeVersion: number | undefined;
  onSelect: (generation: Generation) => void;
}

export function GenerationHistory({ generations, activeVersion, onSelect }: GenerationHistoryProps) {
  if (generations.length <= 1) return null;

  return (
    <div className="rounded-xl border border-base-hairline bg-base-panel p-4 shadow-panel">
      <div className="mb-3 flex items-center justify-between">
        <span className="font-mono text-[11px] uppercase tracking-[0.14em] text-ink-faint">
          Generation history
        </span>
        <span className="font-mono text-[10px] text-ink-faint">last {generations.length} kept</span>
      </div>
      <div className="flex flex-wrap gap-2">
        {generations.map((gen) => {
          const isActive = gen.version === activeVersion;
          return (
            <button
              key={gen.id}
              onClick={() => onSelect(gen)}
              className={[
                "flex items-center gap-2 rounded-lg border px-3 py-1.5 text-xs transition-colors",
                isActive
                  ? "border-tally bg-tally/15 text-tally"
                  : "border-base-hairline bg-base-raised text-ink-muted hover:border-scope",
              ].join(" ")}
            >
              <span className="h-1.5 w-1.5 rounded-full bg-scope" />
              Generation {gen.version}
              <span className="text-ink-faint">
                {new Date(gen.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
