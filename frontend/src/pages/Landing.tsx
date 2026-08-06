import { useAuth } from "../context/AuthContext";

export function Landing() {
  const { loginDemo, loading, error } = useAuth();

  return (
    <div className="flex min-h-screen items-center justify-center px-6">
      <div className="w-full max-w-md">
        <div className="mb-8 flex items-center gap-2.5">
          <span className="h-2.5 w-2.5 rounded-full bg-tally shadow-[0_0_10px_2px_rgba(242,169,59,0.5)]" />
          <span className="font-mono text-[11px] uppercase tracking-[0.2em] text-ink-faint">
            On air
          </span>
        </div>

        <h1 className="font-display text-4xl font-bold leading-tight text-ink">CreatorOS AI</h1>
        <p className="mt-2 text-lg text-ink-muted">Build. Optimize. Publish. Grow.</p>
        <p className="mt-4 text-sm text-ink-muted">
          Six specialized AI agents take a raw idea from trend research to a
          publish-ready asset package — title, script, thumbnail concepts, SEO
          metadata and a publishing plan, chained in one pipeline.
        </p>

        <button
          onClick={loginDemo}
          disabled={loading}
          className="mt-8 w-full rounded-lg bg-tally px-5 py-3 font-display text-sm font-semibold text-base transition-opacity hover:opacity-90 disabled:opacity-50"
        >
          {loading ? "Connecting…" : "Enter demo workspace"}
        </button>

        {error && (
          <p className="mt-3 rounded-lg border border-alert/40 bg-alert/10 px-3 py-2 text-sm text-alert">
            {error} — is the backend running at the configured API URL?
          </p>
        )}

        <p className="mt-4 text-center font-mono text-[11px] text-ink-faint">
          No account needed — this creates a sandboxed demo project.
        </p>
      </div>
    </div>
  );
}
