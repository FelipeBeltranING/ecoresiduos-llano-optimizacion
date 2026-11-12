# AGENTS.md

Web app for optimizing an agro-waste logistics network (Meta, Colombia). FastAPI backend +
React SPA, Spanish domain names. There is no root package manifest: run every command inside
`backend/` or `frontend/`.

## Repository shape

- `backend/app/api/v1/routers/` → `services/` → `repositories/` → `db/models/`.
  API prefix is `/api/v1`.
- `backend/app/optimizacion/` is pure Python (NumPy/PuLP only) and must not import FastAPI or
  SQLAlchemy. `contratos.py` is the adapter boundary used by `ejecucion_service`.
  `exacto/` solves with PuLP + CBC; `genetico/` has the GA; `sensibilidad/` has scenario analysis.
- `backend/alembic/versions/` is the only way schemas change (V1–V4). Migrations enable RLS.
- `frontend/` is a Vite SPA. Routes live in `src/router.tsx`; nav metadata in
  `src/navigation.ts`. Adding a page requires editing both.
- `frontend/src/api/tipos.ts` manually mirrors backend Pydantic schemas (no OpenAPI codegen);
  `hooks.ts` wraps each endpoint with TanStack Query. Update both by hand when the API changes.
- `backend/tests/utilidades.py` is the canonical in-memory fixture. Acceptance tests pin
  `Z_OPTIMO_CASO_BASE = 64_691_000` and `Z_OPTIMO_CON_ACOPIOS = 61_761_025`; changing solver or
  seed data usually means updating those constants and their assertions.

## Backend commands (run from `backend/`)

```bash
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1                         # PowerShell; POSIX: source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env                               # then fill DATABASE_URL
alembic upgrade head
uvicorn app.main:app --reload                      # http://localhost:8000/docs
```

CI order is lint → migrations → tests:

```bash
ruff check .
alembic upgrade head
pytest --cov=app --cov-report=term-missing
```

Targeted tests (always from `backend/`, because `pythonpath = ["."]` and `from tests...`):

```bash
pytest tests/unit/test_red.py -q
pytest tests/unit/test_red.py::test_validacion_caso_base
```

## Frontend commands (run from `frontend/`)

```bash
npm ci                 # CI uses Node 22; package requires >=20.19
npm run dev            # strict port 5173
npm run lint
npm run test           # vitest run
npm run build          # tsc -b && vite build — this is the only typecheck
npx vitest run src/lib/format.test.ts
```

Tests are colocated (`src/**/*.test.ts(x)`), jsdom + Testing Library, setup in
`src/test/setup.ts`. `@/` aliases `src/` in both TS and Vite.

## Environment / operational gotchas

- `backend/.env` is auto-loaded by pydantic-settings and anchored to `backend/`; root `.env`
  only feeds `docker compose`. Only `VITE_*` vars reach the frontend.
- `DATABASE_URL` is **required** by `Settings`, and importing `app.main` triggers it. With no
  `backend/.env`, full `pytest` fails at collection (e.g. `test_health.py`), not just integration
  tests. For unit-only runs any dummy `DATABASE_URL` is enough because the engine
  connects lazily.
- Integration tests need `TEST_DATABASE_URL` and apply Alembic migrations themselves. They skip
  when it is unset and **abort** if the URL contains `supabase` (never point them at Supabase).
- Supabase must use the **Session pooler on port 5432**, not the transaction pooler (6543):
  psycopg 3 prepared statements break on it.
- `ruff` explicitly excludes `app/optimizacion/{exacto,genetico,sensibilidad}`. A green
  `ruff check .` does not mean those files were linted.
- PuLP is pinned `<4`: the code uses the classic API (`pulp.LpVariable(..., lowBound=0)`).
  PuLP 4 removed it.
- Only `app/services/datos/*.json` is declared as package data. New runtime JSON must live
  there (or update `pyproject.toml`) to be included in built wheels.
- Seed data is loaded through `POST /api/v1/datos/caso-base`, `/datos/acopios` and
  `/datos/caso-real`, not through migrations. `python scripts/generar_caso_real.py` regenerates
  the real case (needs internet/OSRM).
- `docker compose up -d --build` starts Postgres 17 + API and runs migrations on API startup.

## Conventions

- Python: PEP 8 via ruff, 100 columns, mandatory type hints, Spanish identifiers. Use short `#`
  section comments; the project convention is **no docstrings**.
- TypeScript: Prettier (`printWidth` 100, double quotes, semicolons, trailing commas), ESLint,
  PascalCase components, `useX` hooks.
- Commits: Conventional Commits in Spanish (`feat(genetico): agrega cruce de dos puntos`).
  Branch from `develop` as `feature/HU-xx-descripcion`; PRs need 1 approval and green CI.
  Never commit `.env` or Supabase credentials.
- GA acceptance tests (`test_aceptacion_genetico.py`) run many generations (10 seeds for the
  gap test) and are the slow part of the suite; run targeted files while iterating.

## Docs

`README.md` is the product overview but trails the code — `backend/app/main.py` and
`backend/app/api/v1/routers/` are the source of truth for endpoints (e.g. HU-20 `/criticidad`
is newer than the README table). `CONTRIBUTING.md` has the workflow/DoR/DoD.
`docs/guias/` explains the optimizer contracts; `docs/backlog/backlog.json` is the backlog.
