import { buildMarkdown, buildScriptText, copyToClipboard, downloadTextFile } from "../lib/export";
import type { Generation } from "../lib/types";

interface ExportCenterProps {
  generation: Generation;
  topic: string;
  onToast: (text: string, tone?: "success" | "error") => void;
}

export function ExportCenter({ generation, topic, onToast }: ExportCenterProps) {
  const slug = topic.trim().toLowerCase().replace(/[^a-z0-9]+/g, "-").slice(0, 40) || "project";

  async function handleCopyScript() {
    try {
      await copyToClipboard(buildScriptText(generation));
      onToast("Script copied to clipboard");
    } catch {
      onToast("Could not copy — clipboard permission denied", "error");
    }
  }

  function handleDownloadMarkdown() {
    downloadTextFile(`${slug}-v${generation.version}.md`, buildMarkdown(generation, topic), "text/markdown");
    onToast("Markdown package downloaded");
  }

  function handleDownloadJson() {
    downloadTextFile(
      `${slug}-v${generation.version}.json`,
      JSON.stringify(generation.result, null, 2),
      "application/json"
    );
    onToast("JSON package downloaded");
  }

  const buttons = [
    { label: "Copy script", onClick: handleCopyScript },
    { label: "Download Markdown", onClick: handleDownloadMarkdown },
    { label: "Download JSON", onClick: handleDownloadJson },
  ];

  return (
    <div className="rounded-xl border border-base-hairline bg-base-panel p-4 shadow-panel">
      <div className="mb-3 flex items-center justify-between">
        <span className="font-mono text-[11px] uppercase tracking-[0.14em] text-ink-faint">
          Export package
        </span>
        <span className="rounded-full border border-scope-dim bg-scope/10 px-2 py-0.5 font-mono text-[10px] text-scope">
          Ready
        </span>
      </div>
      <div className="flex flex-wrap gap-2">
        {buttons.map((b) => (
          <button
            key={b.label}
            onClick={b.onClick}
            className="rounded-lg border border-base-hairline bg-base-raised px-3 py-2 text-sm text-ink-muted transition-colors hover:border-scope hover:text-ink"
          >
            {b.label}
          </button>
        ))}
      </div>
    </div>
  );
}
