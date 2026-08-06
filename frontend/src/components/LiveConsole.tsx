import { useEffect, useRef } from "react";

export interface LogLine {
  id: number;
  text: string;
  tone: "active" | "done" | "error" | "info";
}

export function LiveConsole({ lines }: { lines: LogLine[] }) {
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [lines.length]);

  if (lines.length === 0) return null;

  return (
    <div className="max-h-48 overflow-y-auto rounded-lg border border-base-hairline bg-black/30 p-3 font-mono text-xs">
      {lines.map((line) => (
        <div
          key={line.id}
          className={[
            "py-0.5 transition-opacity duration-300",
            line.tone === "active" && "text-tally",
            line.tone === "done" && "text-scope",
            line.tone === "error" && "text-alert",
            line.tone === "info" && "text-ink-faint",
          ]
            .filter(Boolean)
            .join(" ")}
        >
          <span className="mr-2 text-ink-faint">{">"}</span>
          {line.text}
        </div>
      ))}
      <div ref={endRef} />
    </div>
  );
}
