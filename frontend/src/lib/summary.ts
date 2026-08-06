import type { Generation } from "./types";

export interface SummaryStats {
  topic: string;
  pipelineSeconds: number;
  estimatedWords: number;
  model: string;
  successRate: number; // 0-100
  exportReady: boolean;
}

export interface QualityScores {
  seoScore: number;
  hookStrength: number;
  ctrPotential: number;
  audienceMatch: number;
  publishingReadiness: number;
}

const EXPECTED_STEPS = 6;

export function computeSummaryStats(generation: Generation): SummaryStats {
  const steps = Object.values(generation.result.steps);
  const pipelineSeconds = steps.reduce((sum, s) => sum + (s.elapsed_seconds ?? 0), 0);
  const totalChars = steps.reduce((sum, s) => sum + (s.char_count ?? 0), 0);
  // ~5.5 chars/word average for English — a rough estimate, not a real token/word count.
  const estimatedWords = Math.round(totalChars / 5.5);
  const model = steps[0]?.model ?? "unknown";

  return {
    topic: generation.result.topic,
    pipelineSeconds,
    estimatedWords,
    model,
    successRate: Math.round((steps.length / EXPECTED_STEPS) * 100),
    exportReady: steps.length === EXPECTED_STEPS,
  };
}

/**
 * Heuristic quality scores — NOT model-generated judgments. Simple rule-based
 * estimates from the shape of the output (counts, lengths, an explicit
 * clickability_score the Thumbnail Strategist already returns). Always
 * labeled "Estimated" in the UI per the product spec — these should never
 * be presented as if an AI evaluated content quality.
 */
export function computeQualityScores(generation: Generation): QualityScores {
  const pkg = generation.result.final_package;
  const thumbOutput = generation.result.steps["thumbnail_strategist"]?.output as
    | { clickability_score?: number }
    | undefined;

  const seoScore = clamp(
    pkg.tags.length * 8 + pkg.chapters.length * 6 + (pkg.description.length > 60 ? 20 : 10) + pkg.hashtags.length * 5
  );

  const hookLen = pkg.hook.length;
  const hookStrength = clamp(
    40 + Math.min(hookLen, 80) * 0.5 + (/[?!]/.test(pkg.hook) ? 10 : 0)
  );

  const ctrPotential = clamp(thumbOutput?.clickability_score ?? 55 + pkg.thumbnail_concepts.length * 10);

  const filledFields = [pkg.recommended_title, pkg.hook, pkg.description].filter(Boolean).length;
  const audienceMatch = clamp(60 + filledFields * 10);

  const readinessFields = [
    pkg.recommended_title,
    pkg.description,
    pkg.tags.length > 0,
    pkg.chapters.length > 0,
    pkg.publishing_checklist.length > 0,
    pkg.best_publish_time,
  ];
  const publishingReadiness = clamp(
    Math.round((readinessFields.filter(Boolean).length / readinessFields.length) * 100)
  );

  return { seoScore, hookStrength, ctrPotential, audienceMatch, publishingReadiness };
}

function clamp(n: number): number {
  return Math.max(0, Math.min(100, Math.round(n)));
}
