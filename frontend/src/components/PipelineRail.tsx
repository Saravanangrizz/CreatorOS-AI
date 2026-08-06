import { PIPELINE_STAGES } from "../lib/types";

type StageStatus = "pending" | "active" | "done";

interface PipelineRailProps {
  /** number of stages completed so far (0-6) */
  completedCount: number;
  /** true while a generation is in flight */
  isRunning: boolean;
  activeStage: string | null;
  onSelectStage?: (key: string) => void;
  selectedStage?: string | null;
  /** elapsed seconds per completed stage key, for the mono readout under each dot */
  elapsedByStage?: Record<string, number>;
}

function statusFor(index: number, completedCount: number, isRunning: boolean): StageStatus {
  if (index < completedCount) return "done";
  if (index === completedCount && isRunning) return "active";
  return "pending";
}

export function PipelineRail({
  completedCount,
  isRunning,
  activeStage,
  onSelectStage,
  selectedStage,
  elapsedByStage,
}: PipelineRailProps) {
  const fillPct = (completedCount / PIPELINE_STAGES.length) * 100;

  return (
    <div className="rounded-xl border border-base-hairline bg-base-panel px-5 py-4 shadow-panel">
      <div className="mb-3 flex items-center justify-between">
        <span className="font-mono text-[11px] uppercase tracking-[0.18em] text-ink-faint">
          Pipeline Rail
        </span>
        <span className="font-mono text-[11px] tabular-nums text-ink-faint">
          {completedCount}/{PIPELINE_STAGES.length} STAGES
        </span>
      </div>

      {/* the console rail track */}
      <div className="relative">
        <div className="absolute left-0 right-0 top-[13px] h-[2px] bg-base-hairline" />
        <div
          className="absolute left-0 top-[13px] h-[2px] bg-scope transition-all duration-700 ease-out"
          style={{ width: `${fillPct}%` }}
        />
        <ol className="relative grid grid-cols-6 gap-1">
          {PIPELINE_STAGES.map((stage, i) => {
            const status = statusFor(i, completedCount, isRunning);
            const isSelected = selectedStage === stage.key;
            return (
              <li key={stage.key} className="flex flex-col items-center gap-2">
                <button
                  type="button"
                  disabled={status === "pending"}
                  onClick={() => onSelectStage?.(stage.key)}
                  aria-current={activeStage === stage.key}
                  className={[
                    "relative z-10 h-[26px] w-[26px] rounded-full border transition-colors",
                    status === "done" &&
                      "border-scope bg-scope/20 shadow-[0_0_0_3px_rgba(79,209,197,0.12)]",
                    status === "active" && "border-tally bg-tally/20 animate-pulse",
                    status === "pending" && "border-base-hairline bg-base-raised",
                    isSelected && "ring-2 ring-tally ring-offset-2 ring-offset-base-panel",
                    status !== "pending" ? "cursor-pointer" : "cursor-default",
                  ]
                    .filter(Boolean)
                    .join(" ")}
                >
                  <span
                    className={[
                      "absolute inset-[6px] rounded-full",
                      status === "done" && "bg-scope",
                      status === "active" && "bg-tally",
                      status === "pending" && "bg-base-hairline",
                    ]
                      .filter(Boolean)
                      .join(" ")}
                  />
                </button>
                <span
                  className={[
                    "font-mono text-[10px] uppercase tracking-wide",
                    status === "pending" ? "text-ink-faint" : "text-ink-muted",
                  ].join(" ")}
                >
                  {stage.label}
                </span>
                <span className="h-3 font-mono text-[9px] tabular-nums text-scope">
                  {status === "done" && elapsedByStage?.[stage.key] != null
                    ? `${elapsedByStage[stage.key].toFixed(1)}s`
                    : status === "active"
                    ? "running…"
                    : ""}
                </span>
              </li>
            );
          })}
        </ol>
      </div>
    </div>
  );
}
