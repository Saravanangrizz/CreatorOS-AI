const SECTIONS: { title: string; items: string[] }[] = [
  {
    title: "Multi-AI orchestration",
    items: ["OpenAI GPT models", "Anthropic Claude", "Perplexity AI", "Local LLM support", "Automatic provider selection"],
  },
  {
    title: "Creator integrations",
    items: ["YouTube Studio", "TikTok", "Instagram", "X (Twitter)", "LinkedIn", "Notion", "Google Docs"],
  },
  {
    title: "AI media generation",
    items: ["AI thumbnails", "AI video storyboard", "AI shorts generator", "Voice-over generation", "Auto subtitle generation"],
  },
  {
    title: "Collaboration",
    items: ["Team workspaces", "Comments", "Shared projects", "Full audit-trail version history"],
  },
  {
    title: "Analytics",
    items: ["Live SEO scoring", "Competitor analysis", "Performance prediction", "Trend forecasting", "Audience analytics"],
  },
];

export function Roadmap({ onClose }: { onClose: () => void }) {
  return (
    <div className="fixed inset-0 z-40 flex items-start justify-center overflow-y-auto bg-black/60 px-4 py-10">
      <div className="w-full max-w-2xl rounded-xl border border-base-hairline bg-base-panel p-6 shadow-panel">
        <div className="mb-1 flex items-center justify-between">
          <h2 className="font-display text-xl font-bold text-ink">Future Roadmap</h2>
          <button
            onClick={onClose}
            className="rounded-md border border-base-hairline px-2 py-1 font-mono text-[11px] text-ink-faint hover:text-ink"
          >
            Close
          </button>
        </div>
        <p className="mb-6 text-sm text-ink-muted">
          Planned future features — not implemented in this hackathon build. Today's
          build runs entirely on Gemini as the single production AI provider.
        </p>

        <div className="space-y-5">
          {SECTIONS.map((section) => (
            <div key={section.title}>
              <h3 className="mb-2 font-mono text-[11px] uppercase tracking-[0.14em] text-tally">
                {section.title}
              </h3>
              <ul className="grid grid-cols-1 gap-1 text-sm text-ink-muted sm:grid-cols-2">
                {section.items.map((item) => (
                  <li key={item} className="flex items-center gap-2">
                    <span className="h-1 w-1 rounded-full bg-ink-faint" />
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
