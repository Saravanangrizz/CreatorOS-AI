# CreatorOS AI — Backend

FastAPI backend implementing the multi-agent creator workflow pipeline
(Trend Analyst → Research Agent → Script Writer → Thumbnail Strategist →
SEO Specialist → Publishing Planner), plus a standalone Analytics Coach.

## Architecture

```
Routes (app/api)          <- thin, no business logic
   |
Services (app/services)   <- business logic, DB transactions
   |
Orchestrator (app/agents) <- runs the agent pipeline, chains context
   |
AI Provider (app/core/ai_provider.py) <- Gemini / OpenAI / Claude / Mock
   |
Models (app/models)       <- SQLAlchemy ORM (SQLite for this build)
```

## Run locally

```bash
cd backend
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
cp .env.example .env
```

To try it with **canned demo responses** (no API key needed), leave
`DEMO_MODE=true` in `.env` and run:

```bash
./venv/bin/uvicorn app.main:app --reload
```

To make **real Gemini calls**, edit `.env`:

```
DEMO_MODE=false
AI_PROVIDER=gemini
GEMINI_API_KEY=your-real-key-here
```

Then hit the docs at `http://127.0.0.1:8000/docs` to try it interactively,
or:

```bash
curl -X POST http://127.0.0.1:8000/api/auth/demo-login
# copy the access_token, then:
curl -X POST http://127.0.0.1:8000/api/projects \
  -H "Authorization: Bearer <token>" -H "Content-Type: application/json" \
  -d '{"topic": "how to edit vlogs faster"}'
# copy the returned project id, then:
curl -X POST http://127.0.0.1:8000/api/projects/<project_id>/generate \
  -H "Authorization: Bearer <token>"
```

## Tests

```bash
./venv/bin/python tests/test_orchestrator.py   # pipeline logic, no HTTP
./venv/bin/python tests/test_api_smoke.py      # full HTTP flow
```

## Switching AI providers

Only `AI_PROVIDER=gemini` is fully implemented against a live API today.
`OpenAIProvider` and `ClaudeProvider` in `app/core/ai_provider.py` already
implement the same interface — adding a key and the SDK call in their
`generate()` method is the only change needed; no agent or route code
changes.

## Roadmap (post-hackathon)

- Postgres + Alembic migrations (swap-in, ORM layer unchanged)
- Redis caching for repeated generations
- Real OAuth, refresh tokens, rate limiting
- Template marketplace, prompt library, project export (MD/DOCX/PDF/JSON)
