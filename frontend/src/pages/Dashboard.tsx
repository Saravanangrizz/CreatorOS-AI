import { useEffect, useState, type FormEvent } from "react";
import { useAuth } from "../context/AuthContext";
import { api, ApiError } from "../lib/api";
import type { AgentStepOutput, Generation, Project } from "../lib/types";
import { DEFAULT_SETTINGS, type GenerationSettings } from "../lib/types";
import { PipelineRail } from "../components/PipelineRail";
import { StageDetail } from "../components/StageDetail";
import { FinalPackagePanel } from "../components/FinalPackagePanel";
import { SettingsPanel } from "../components/SettingsPanel";
import { LiveConsole, type LogLine } from "../components/LiveConsole";
import { GenerationHistory } from "../components/GenerationHistory";
import { SummaryDashboard } from "../components/SummaryDashboard";
import { ExportCenter } from "../components/ExportCenter";
import { ToastStack, type Toast } from "../components/Toast";
import { Roadmap } from "./Roadmap";

let logIdCounter = 0;
let toastIdCounter = 0;

export function Dashboard() {
  const { logout } = useAuth();
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [newTopic, setNewTopic] = useState("");
  const [creating, setCreating] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [generations, setGenerations] = useState<Generation[]>([]);
  const [generation, setGeneration] = useState<Generation | null>(null);
  const [selectedStage, setSelectedStage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loadingProjects, setLoadingProjects] = useState(true);
  const [settings, setSettings] = useState<GenerationSettings>(DEFAULT_SETTINGS);
  const [showRoadmap, setShowRoadmap] = useState(false);
  const [toasts, setToasts] = useState<Toast[]>([]);

  // Live execution state — populated as SSE events arrive during a run
  const [liveSteps, setLiveSteps] = useState<Record<string, AgentStepOutput>>({});
  const [liveActiveKey, setLiveActiveKey] = useState<string | null>(null);
  const [logLines, setLogLines] = useState<LogLine[]>([]);

  function pushLog(text: string, tone: LogLine["tone"] = "info") {
    logIdCounter += 1;
    setLogLines((prev) => [...prev.slice(-49), { id: logIdCounter, text, tone }]);
  }

  function pushToast(text: string, tone?: Toast["tone"]) {
    toastIdCounter += 1;
    setToasts((prev) => [...prev, { id: toastIdCounter, text, tone }]);
  }

  function dismissToast(id: number) {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }

  async function refreshProjects(selectAfter?: string) {
    try {
      const list = await api.listProjects();
      setProjects(list);
      if (selectAfter) setSelectedId(selectAfter);
      else if (!selectedId && list.length) setSelectedId(list[0].id);
    } catch (err) {
      setError(describeError(err));
    } finally {
      setLoadingProjects(false);
    }
  }

  useEffect(() => {
    refreshProjects();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    setGeneration(null);
    setGenerations([]);
    setSelectedStage(null);
    setLiveSteps({});
    setLogLines([]);
    if (!selectedId) return;
    api
      .listGenerations(selectedId)
      .then((gens) => {
        setGenerations(gens);
        if (gens.length) setGeneration(gens[0]);
      })
      .catch((err) => setError(describeError(err)));
  }, [selectedId]);

  async function handleCreate(e: FormEvent) {
    e.preventDefault();
    if (!newTopic.trim()) return;
    setCreating(true);
    setError(null);
    try {
      const project = await api.createProject(newTopic.trim());
      setNewTopic("");
      await refreshProjects(project.id);
    } catch (err) {
      setError(describeError(err));
    } finally {
      setCreating(false);
    }
  }

  async function handleGenerate() {
    if (!selectedId) return;
    setGenerating(true);
    setError(null);
    setLiveSteps({});
    setLiveActiveKey(null);
    setLogLines([]);
    setSelectedStage(null);
    pushLog(`Starting pipeline for "${projects.find((p) => p.id === selectedId)?.topic ?? ""}"…`);

    try {
      await api.generateStream(selectedId, settings, (event) => {
        if (event.type === "stage_start") {
          setLiveActiveKey(event.agent);
          pushLog(`${event.display_name} — working…`, "active");
        } } else if (event.type === "stage_done") {
          setLiveSteps((prev) => ({ ...prev, [event.agent]: event }));
          setLiveActiveKey(null);
          const retryNote = event.attempts && event.attempts > 1 ? ` — recovered after ${event.attempts} attempts` : "";
          pushLog(
            `${event.display_name} — done in ${event.elapsed_seconds.toFixed(1)}s (${event.char_count} chars)${retryNote}`,"done");
        } else if (event.type === "final_package") {
          pushLog("Assembling final package…");
        } else if (event.type === "complete") {
          pushLog(`Pipeline complete — v${event.version}`, "done");
          pushToast(`Generation v${event.version} complete`, "success");
        } else if (event.type === "error") {
          pushLog(`Error: ${event.detail}`, "error");
          setError(event.detail);
          pushToast("Pipeline failed", "error");
        }
      });

      const gens = await api.listGenerations(selectedId);
      setGenerations(gens);
      if (gens.length) setGeneration(gens[0]);
      await refreshProjects(selectedId);
    } catch (err) {
      setError(describeError(err));
      pushLog(describeError(err), "error");
    } finally {
      setGenerating(false);
      setLiveActiveKey(null);
    }
  }

  const selectedProject = projects.find((p) => p.id === selectedId) ?? null;

  const stepsForDisplay: Record<string, AgentStepOutput> = generating
    ? liveSteps
    : generation?.result.steps ?? {};
  const completedCount = Object.keys(stepsForDisplay).length;
  const elapsedByStage = Object.fromEntries(
    Object.entries(stepsForDisplay)
      .filter(([, s]) => s.elapsed_seconds != null)
      .map(([k, s]) => [k, s.elapsed_seconds as number])
  );
  const activeStep = selectedStage ? stepsForDisplay[selectedStage] : null;

  return (
    <div className="min-h-screen">
      <header className="flex items-center justify-between border-b border-base-hairline px-6 py-4">
        <div className="flex items-center gap-2.5">
          <span className="h-2 w-2 rounded-full bg-tally shadow-[0_0_8px_2px_rgba(242,169,59,0.5)]" />
          <span className="font-display text-sm font-bold tracking-wide text-ink">
            CreatorOS AI
          </span>
        </div>
        <div className="flex items-center gap-5">
          <button
            onClick={() => setShowRoadmap(true)}
            className="font-mono text-[11px] uppercase tracking-wide text-ink-faint hover:text-ink"
          >
            Roadmap
          </button>
          <button
            onClick={logout}
            className="font-mono text-[11px] uppercase tracking-wide text-ink-faint hover:text-ink"
          >
            Sign out
          </button>
        </div>
      </header>

      <div className="mx-auto grid max-w-7xl grid-cols-1 gap-6 px-6 py-6 lg:grid-cols-[260px_1fr_280px]">
        {/* Sidebar: workspace */}
        <aside className="space-y-4">
          <form onSubmit={handleCreate} className="space-y-2">
            <label className="font-mono text-[11px] uppercase tracking-[0.14em] text-ink-faint">
              New project
            </label>
            <input
              value={newTopic}
              onChange={(e) => setNewTopic(e.target.value)}
              placeholder="e.g. batch editing shorts"
              className="w-full rounded-lg border border-base-hairline bg-base-panel px-3 py-2 text-sm text-ink placeholder:text-ink-faint focus:border-scope"
            />
            <button
              type="submit"
              disabled={creating || !newTopic.trim()}
              className="w-full rounded-lg border border-base-hairline bg-base-raised px-3 py-2 text-sm font-medium text-ink transition-colors hover:border-scope disabled:opacity-40"
            >
              {creating ? "Creating…" : "+ Create project"}
            </button>
          </form>

          <div className="space-y-1">
            <p className="font-mono text-[11px] uppercase tracking-[0.14em] text-ink-faint">
              Projects
            </p>
            {loadingProjects && <p className="text-sm text-ink-faint">Loading…</p>}
            {!loadingProjects && projects.length === 0 && (
              <p className="text-sm text-ink-faint">
                No projects yet — create one above to start the pipeline.
              </p>
            )}
            <ul className="space-y-1">
              {projects.map((p) => (
                <li key={p.id}>
                  <button
                    onClick={() => setSelectedId(p.id)}
                    className={[
                      "flex w-full items-center justify-between rounded-lg px-3 py-2 text-left text-sm transition-colors",
                      p.id === selectedId
                        ? "bg-base-raised text-ink"
                        : "text-ink-muted hover:bg-base-panel",
                    ].join(" ")}
                  >
                    <span className="truncate">{p.topic}</span>
                    <StatusDot status={p.status} />
                  </button>
                </li>
              ))}
            </ul>
          </div>
        </aside>

        {/* Main canvas */}
        <main className="space-y-6">
          {error && (
            <div className="rounded-lg border border-alert/40 bg-alert/10 px-3 py-2 text-sm text-alert">
              {error}
            </div>
          )}

          {!selectedProject && (
            <div className="rounded-xl border border-dashed border-base-hairline p-10 text-center text-ink-faint">
              Select or create a project to open the pipeline.
            </div>
          )}

          {selectedProject && (
            <>
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="font-display text-2xl font-semibold text-ink">
                    {selectedProject.topic}
                  </h1>
                  <p className="font-mono text-[11px] uppercase tracking-wide text-ink-faint">
                    v{generation?.version ?? 0} · {selectedProject.status}
                  </p>
                </div>
                <button
                  onClick={handleGenerate}
                  disabled={generating}
                  className="rounded-lg bg-tally px-4 py-2.5 font-display text-sm font-semibold text-base transition-opacity hover:opacity-90 disabled:opacity-50"
                >
                  {generating
                    ? "Running pipeline…"
                    : generation
                    ? "Regenerate"
                    : "Run pipeline"}
                </button>
              </div>

              <PipelineRail
                completedCount={completedCount}
                isRunning={generating}
                activeStage={liveActiveKey}
                elapsedByStage={elapsedByStage}
                selectedStage={selectedStage}
                onSelectStage={setSelectedStage}
              />

              <LiveConsole lines={logLines} />

              {!generating && (
                <GenerationHistory
                  generations={generations}
                  activeVersion={generation?.version}
                  onSelect={(gen) => {
                    setGeneration(gen);
                    setSelectedStage(null);
                  }}
                />
              )}

              {!generation && !generating && (
                <div className="rounded-xl border border-dashed border-base-hairline p-10 text-center text-ink-faint">
                  No generation yet — run the pipeline to produce a full asset
                  package.
                </div>
              )}

              {activeStep && <StageDetail step={activeStep} />}

              {generation && !activeStep && !generating && (
                <>
                  <FinalPackagePanel pkg={generation.result.final_package} />
                  <SummaryDashboard generation={generation} />
                  <ExportCenter
                    generation={generation}
                    topic={selectedProject.topic}
                    onToast={pushToast}
                  />
                </>
              )}
            </>
          )}
        </main>

        {/* Settings sidebar */}
        <aside>
          <SettingsPanel settings={settings} onChange={setSettings} disabled={generating} />
        </aside>
      </div>

      {showRoadmap && <Roadmap onClose={() => setShowRoadmap(false)} />}
      <ToastStack toasts={toasts} onDismiss={dismissToast} />
    </div>
  );
}

function StatusDot({ status }: { status: Project["status"] }) {
  const color =
    status === "ready"
      ? "bg-scope"
      : status === "generating"
      ? "bg-tally animate-pulse"
      : status === "published"
      ? "bg-scope"
      : "bg-ink-faint";
  return <span className={`h-1.5 w-1.5 shrink-0 rounded-full ${color}`} />;
}

function describeError(err: unknown): string {
  if (err instanceof ApiError) return err.message;
  if (err instanceof Error) return err.message;
  return "Something went wrong";
}
