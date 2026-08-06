# CreatorOS AI

**Build. Optimize. Publish. Grow.**

An AI creator operating system for YouTube — six specialized agents
(Trend Analyst, Research Agent, Script Writer, Thumbnail Strategist, SEO
Specialist, Publishing Planner) collaborate in a single pipeline to turn a
raw topic idea into a publish-ready asset package, plus a standalone
Analytics Coach for post-publish metrics.

Built for the [YouTube Automation Hackathon](https://youtube-automate-hackathon.devpost.com/).

## Quick start

Two terminals:

```bash
# Terminal 1 — backend
cd backend
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
cp .env.example .env
./venv/bin/uvicorn app.main:app --reload

# Terminal 2 — frontend
cd frontend
npm install
cp .env.example .env
npm run dev
```

Open `http://localhost:5173`, click **Enter demo workspace**, create a
project, and run the pipeline. Runs entirely on canned demo responses by
default (`DEMO_MODE=true`) — no API key required to try it.

To see it run against a real model, set `DEMO_MODE=false` and add your
Gemini key in `backend/.env` — see `backend/README.md` for details.

## Architecture

```
React/TS/Vite/Tailwind  →  FastAPI  →  Orchestrator  →  AI Provider (Gemini/OpenAI/Claude/Mock)
                              ↓
                         SQLite (SQLAlchemy)
```

- **Multi-agent orchestration**: agents run in sequence, each seeing the
  prior agents' real output (see `backend/app/agents/orchestrator.py`)
- **Switchable AI provider**: one interface, swap providers via env var,
  no agent code changes (see `backend/app/core/ai_provider.py`)
- **Explainable recommendations**: every agent returns a `reasoning`
  field, surfaced in the UI's stage detail panel
- **Free version history**: every pipeline run is stored as a new
  `Generation` row — no separate versioning system needed

## Status

Backend: complete and tested (unit + full HTTP flow).
Frontend: dashboard, pipeline rail, stage detail, final package view — built and verified (typecheck + build + module transform checks).

See `/backend/README.md` and project roadmap notes in-code for what's
intentionally deferred past the hackathon deadline.
