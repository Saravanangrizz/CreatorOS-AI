import { computeQualityScores, computeSummaryStats } from "../lib/summary";
import type { Generation } from "../lib/types";

function ScoreBar({ label, value }: { label: string; value: number }) {
  const color = value >= 75 ? "bg-scope" : value >= 50 ? "bg-tally" : "bg-alert";
  return (
    <div>
      <div className="mb-1 flex items-center justify-between">
        <span className="text-xs text-ink-muted">{label}</span>
        <span className="font-mono text-xs tabular-nums text-ink">{value}</span>
      </div>
      <div className="h-1.5 overflow-hidden rounded-full bg-base-raised">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${value}%` }} />
      </div>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-ink-faint">{label}</p>
      <p className="mt-0.5 font-display text-lg font-semibold text-ink">{value}</p>
    </div>
  );
}

export function SummaryDashboard({ generation }: { generation: Generation }) {
  const stats = computeSummaryStats(generation);
  const scores = computeQualityScores(generation);

  return (
    <div className="rounded-xl border border-scope-dim bg-scope/[0.04] p-5 shadow-panel">
      <div className="mb-4 flex items-center gap-2">
        <span className="h-2 w-2 rounded-full bg-scope" />
        <h3 className="font-mono text-[11px] uppercase tracking-[0.14em] text-scope">
          Project complete
        </h3>
      </div>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <Stat label="Pipeline time" value={`${stats.pipelineSeconds.toFixed(1)}s`} />
        <Stat label="Words generated" value={`~${stats.estimatedWords.toLocaleString()}`} />
        <Stat label="AI model" value={stats.model} />
        <Stat label="Pipeline success" value={`${stats.successRate}%`} />
      </div>

      <div className="mt-5 border-t border-base-hairline pt-4">
        <div className="mb-2 flex items-baseline justify-between">
          <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-ink-faint">
            Estimated content quality
          </p>
          <p className="text-[10px] text-ink-faint">Heuristic — not AI-evaluated</p>
        </div>
        <div className="grid gap-3 sm:grid-cols-2">
          <ScoreBar label="SEO score" value={scores.seoScore} />
          <ScoreBar label="Hook strength" value={scores.hookStrength} />
          <ScoreBar label="CTR potential" value={scores.ctrPotential} />
          <ScoreBar label="Audience match" value={scores.audienceMatch} />
        </div>
        <div className="mt-3">
          <ScoreBar label="Publishing readiness" value={scores.publishingReadiness} />
        </div>
      </div>
    </div>
  );
}
