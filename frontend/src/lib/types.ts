export interface Project {
  id: string;
  topic: string;
  status: "draft" | "generating" | "ready" | "published";
  created_at: string;
  updated_at: string;
}

export interface AgentStepOutput {
  agent: string;
  display_name: string;
  provider: string;
  model: string;
  output: Record<string, unknown> & { reasoning?: string };
  elapsed_seconds?: number;
  char_count?: number;
  attempts?: number;
}

export interface GenerationSettings {
  content_length: "short" | "medium" | "long";
  creativity: "low" | "medium" | "high";
  target_platform: "youtube" | "tiktok" | "instagram" | "blog";
  tone: "professional" | "educational" | "storytelling" | "humorous";
  audience: "beginner" | "intermediate" | "advanced";
}

export const DEFAULT_SETTINGS: GenerationSettings = {
  content_length: "medium",
  creativity: "medium",
  target_platform: "youtube",
  tone: "professional",
  audience: "intermediate",
};

export interface FinalPackage {
  recommended_title: string;
  hook: string;
  description: string;
  tags: string[];
  hashtags: string[];
  chapters: { time: string; label: string }[];
  thumbnail_concepts: { style: string; prompt: string }[];
  publishing_checklist: string[];
  best_publish_time: string;
}

export interface PipelineResult {
  topic: string;
  settings?: GenerationSettings;
  steps: Record<string, AgentStepOutput>;
  final_package: FinalPackage;
}

export interface Generation {
  id: string;
  project_id: string;
  version: number;
  provider: string;
  created_at: string;
  result: PipelineResult;
}

export const PIPELINE_STAGES: { key: string; label: string }[] = [
  { key: "trend_analyst", label: "Trend" },
  { key: "research_agent", label: "Research" },
  { key: "script_writer", label: "Script" },
  { key: "thumbnail_strategist", label: "Thumbnail" },
  { key: "seo_specialist", label: "SEO" },
  { key: "publishing_planner", label: "Publish" },
];
